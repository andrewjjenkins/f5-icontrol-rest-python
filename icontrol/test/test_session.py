# Copyright 2015 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import mock
import pytest

from icontrol import session


@pytest.fixture()
def iCRS():
    fake_iCRS = session.iControlRESTSession('admin', 'admin')
    fake_iCRS.session = mock.MagicMock()
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    fake_iCRS.session.delete.return_value = mock_response
    fake_iCRS.session.get.return_value = mock_response
    fake_iCRS.session.patch.return_value = mock_response
    fake_iCRS.session.post.return_value = mock_response
    fake_iCRS.session.put.return_value = mock_response
    return fake_iCRS


@pytest.fixture()
def uparts():
    parts_dict = {'base_uri': 'https://0.0.0.0/mgmt/tm/root/RESTiface/',
                  'folder': 'BIGCUSTOMER',
                  'instance_name': 'foobar1',
                  'suffix': '/members/m1'}
    return parts_dict


# Test uri component validation
def test_incorrect_uri_construction_bad_scheme(uparts):
    uparts['base_uri'] = 'hryttps://0.0.0.0/mgmt/tm/root/RESTiface/'
    with pytest.raises(session.InvalidScheme) as IS:
        session.generate_bigip_uri(**uparts)
    assert IS.value.message == 'hryttps'


def test_incorrect_uri_construction_bad_mgmt_path(uparts):
    uparts['base_uri'] = 'https://0.0.0.0/magmt/tm/root/RESTiface'
    with pytest.raises(session.InvalidBigIP_ICRURI) as IR:
        session.generate_bigip_uri(**uparts)
    assert IR.value.message ==\
        "The path must start with '/mgmt/tm/'!!  But it's: '/magmt/tm/'"


def test_incorrect_uri_construction_bad_base_nonslash_last(uparts):
    uparts['base_uri'] = 'https://0.0.0.0/mgmt/tm/root/RESTiface'
    with pytest.raises(session.InvalidPrefixCollection) as IR:
        session.generate_bigip_uri(**uparts)
    test_value = "prefix_collections path element must end with '/', but" +\
        " it's: root/RESTiface"
    assert IR.value.message == test_value


def test_incorrect_uri_construction_illegal_slash_folder_char(uparts):
    uparts['folder'] = 'spam/ham'
    with pytest.raises(session.InvalidInstanceNameOrFolder) as II:
        session.generate_bigip_uri(**uparts)
    test_value = "instance names and folders cannot contain '/', but it's: %s"\
                 % uparts['folder']
    assert II.value.message == test_value


def test_incorrect_uri_construction_illegal_tilde_folder_char(uparts):
    uparts['folder'] = 'spam~ham'
    with pytest.raises(session.InvalidInstanceNameOrFolder) as II:
        session.generate_bigip_uri(**uparts)
    test_value = "instance names and folders cannot contain '~', but it's: %s"\
                 % uparts['folder']
    assert II.value.message == test_value


def test_incorrect_uri_construction_illegal_suffix_nonslash_first(uparts):
    uparts['suffix'] = 'ham'
    with pytest.raises(session.InvalidSuffixCollection) as II:
        session.generate_bigip_uri(**uparts)
    test_value = "suffix_collections path element must start with '/', but " +\
                 "it's: %s" % uparts['suffix']
    assert II.value.message == test_value


def test_incorrect_uri_construction_illegal_suffix_slash_last(uparts):
    uparts['suffix'] = '/ham/'
    with pytest.raises(session.InvalidSuffixCollection) as II:
        session.generate_bigip_uri(**uparts)
    test_value = "suffix_collections path element must not end with '/', " +\
                 "but it's: %s" % uparts['suffix']
    assert II.value.message == test_value


# Test uri construction
def test_correct_uri_construction_folderless(uparts):
    uparts['folder'] = ''
    uri = session.generate_bigip_uri(**uparts)
    assert uri == 'https://0.0.0.0/mgmt/tm/root/RESTiface/~foobar1/members/m1'


def test_correct_uri_construction_nameless(uparts):
    uparts['instance_name'] = ''
    uri = session.generate_bigip_uri(**uparts)
    assert uri ==\
        "https://0.0.0.0/mgmt/tm/root/RESTiface/~BIGCUSTOMER/members/m1"


def test_correct_uri_construction_folderless_and_nameless(uparts):
    uparts['folder'] = ''
    uparts['instance_name'] = ''
    uri = session.generate_bigip_uri(**uparts)
    assert uri == "https://0.0.0.0/mgmt/tm/root/RESTiface/members/m1"


def test_correct_uri_construction_folder_name_and_suffixless(uparts):
    uparts['folder'] = ''
    uparts['instance_name'] = ''
    uparts['suffix'] = ''
    uri = session.generate_bigip_uri(**uparts)
    assert uri == "https://0.0.0.0/mgmt/tm/root/RESTiface/"


def test_correct_uri_construction_folderless_and_suffixless(uparts):
    uparts['folder'] = ''
    uparts['suffix'] = ''
    uri = session.generate_bigip_uri(**uparts)
    assert uri == 'https://0.0.0.0/mgmt/tm/root/RESTiface/~foobar1'


def test_correct_uri_construction_nameless_and_suffixless(uparts):
    uparts['instance_name'] = ''
    uparts['suffix'] = ''
    uri = session.generate_bigip_uri(**uparts)
    assert uri == 'https://0.0.0.0/mgmt/tm/root/RESTiface/~BIGCUSTOMER'


# Test exception handling
def test_wrapped_delete_success(iCRS, uparts):
    iCRS.delete(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')


def test_wrapped_delete_207_fail(iCRS, uparts):
    iCRS.session.delete.return_value.status_code = 207
    with pytest.raises(session.iControlUnexpectedHTTPError) as CHE:
        iCRS.delete(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')
    assert CHE.value.message.startswith('207 Unexpected Error: ')


def test_wrapped_get_success(iCRS, uparts):
    iCRS.get(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')


def test_wrapped_get_207_fail(iCRS, uparts):
    iCRS.session.get.return_value.status_code = 207
    with pytest.raises(session.iControlUnexpectedHTTPError) as CHE:
        iCRS.get(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')
    assert CHE.value.message.startswith('207 Unexpected Error: ')


def test_wrapped_patch_success(iCRS, uparts):
    iCRS.patch(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')


def test_wrapped_patch_207_fail(iCRS, uparts):
    iCRS.session.patch.return_value.status_code = 207
    with pytest.raises(session.iControlUnexpectedHTTPError) as CHE:
        iCRS.patch(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')
    assert CHE.value.message.startswith('207 Unexpected Error: ')


def test_wrapped_post_success(iCRS, uparts):
    iCRS.post(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')


def test_wrapped_post_207_fail(iCRS, uparts):
    iCRS.session.post.return_value.status_code = 207
    with pytest.raises(session.iControlUnexpectedHTTPError) as CHE:
        iCRS.post(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')
    assert CHE.value.message.startswith('207 Unexpected Error: ')


def test_wrapped_put_success(iCRS, uparts):
    iCRS.put(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')


def test_wrapped_put_207_fail(iCRS, uparts):
    iCRS.session.put.return_value.status_code = 207
    with pytest.raises(session.iControlUnexpectedHTTPError) as CHE:
        iCRS.put(uparts['base_uri'], 'A_FOLDER_NAME', 'AN_INSTANCE_NAME')
    assert CHE.value.message.startswith('207 Unexpected Error: ')