from __future__ import absolute_import

import tempfile

from django.utils.translation import ugettext_lazy as _

from acls.api import class_permissions
from common.utils import encapsulate, validate_path
from dynamic_search.classes import SearchModel
from history.api import register_history_type
from history.permissions import PERMISSION_HISTORY_VIEW
from main.api import register_diagnostic, register_maintenance_links
from navigation.api import (register_links, register_model_list_columns,
                            register_top_menu)
from navigation.links import link_spacer
from project_setup.api import register_setup
from rest_api.classes import APIEndPoint
from statistics.classes import StatisticNamespace

from documents import settings as document_settings
from .events import (HISTORY_DOCUMENT_CREATED,
                     HISTORY_DOCUMENT_DELETED, HISTORY_DOCUMENT_EDITED)
from .links import (document_clear_image_cache,
                    document_clear_transformations, document_delete,
                    document_download, document_edit,
                    document_history_view, document_list,
                    document_list_recent, document_missing_list,
                    document_multiple_delete,
                    document_multiple_clear_transformations,
                    document_multiple_download,
                    document_multiple_update_page_count, document_page_edit,
                    document_page_navigation_first,
                    document_page_navigation_last,
                    document_page_navigation_next,
                    document_page_navigation_previous,
                    document_page_rotate_left, document_page_rotate_right,
                    document_page_text, document_page_transformation_list,
                    document_page_transformation_create,
                    document_page_transformation_edit,
                    document_page_transformation_delete, document_page_view,
                    document_page_view_reset, document_page_zoom_in,
                    document_page_zoom_out, document_print,
                    document_type_create, document_type_delete,
                    document_type_edit, document_type_filename_create,
                    document_type_filename_delete,
                    document_type_filename_edit, document_type_filename_list,
                    document_type_list, document_type_setup,
                    document_update_page_count, document_version_download,
                    document_version_list, document_version_revert,
                    document_view_advanced, document_view_simple)
from .models import (Document, DocumentPage, DocumentPageTransformation,
                     DocumentType, DocumentTypeFilename, DocumentVersion)
from .permissions import (PERMISSION_DOCUMENT_DELETE,
                          PERMISSION_DOCUMENT_DOWNLOAD,
                          PERMISSION_DOCUMENT_EDIT,
                          PERMISSION_DOCUMENT_NEW_VERSION,
                          PERMISSION_DOCUMENT_PROPERTIES_EDIT,
                          PERMISSION_DOCUMENT_TRANSFORM,
                          PERMISSION_DOCUMENT_VERSION_REVERT,
                          PERMISSION_DOCUMENT_VIEW)
from .settings import THUMBNAIL_SIZE
from .serializers import DocumentSerializer
from .statistics import DocumentStatistics, DocumentUsageStatistics
from .urls import api_urls
from .widgets import document_thumbnail

# History setup
register_history_type(HISTORY_DOCUMENT_CREATED)
register_history_type(HISTORY_DOCUMENT_EDITED)
register_history_type(HISTORY_DOCUMENT_DELETED)

# Register document type links
register_links(DocumentType, [document_type_edit, document_type_filename_list, document_type_delete])
register_links(DocumentTypeFilename, [document_type_filename_edit, document_type_filename_delete])
register_links(['documents:setup_document_type_metadata', 'documents:document_type_filename_delete', 'documents:document_type_create', 'documents:document_type_filename_create', 'documents:document_type_filename_edit', 'documents:document_type_filename_list', 'documents:document_type_list', 'documents:document_type_edit', 'documents:document_type_delete'], [document_type_list, document_type_create], menu_name='secondary_menu')
register_links([DocumentTypeFilename, 'documents:document_type_filename_list', 'documents:document_type_filename_create'], [document_type_filename_create], menu_name='sidebar')

# Register document links
register_links(Document, [document_view_simple, document_edit, document_print, document_delete, document_download, document_clear_transformations, document_update_page_count])
register_links([Document], [link_spacer, document_multiple_clear_transformations, document_multiple_delete, document_multiple_download, document_multiple_update_page_count], menu_name='multi_item_links')

# Document Version links
register_links(DocumentVersion, [document_version_revert, document_version_download])
secondary_menu_links = [document_list_recent, document_list]
register_links(['documents:document_list_recent', 'documents:document_list', 'sources:document_create', 'sources:document_create_multiple', 'sources:upload_interactive', 'sources:staging_file_delete'], secondary_menu_links, menu_name='secondary_menu')
register_links(Document, secondary_menu_links, menu_name='secondary_menu')

# Document page links
register_links(DocumentPage, [
    document_page_transformation_list, document_page_view,
    document_page_text, document_page_edit,
])

# Document page navigation links
register_links(DocumentPage, [
    document_page_navigation_first, document_page_navigation_previous,
    document_page_navigation_next, document_page_navigation_last
], menu_name='related')

register_links(['documents:document_page_view'], [document_page_rotate_left, document_page_rotate_right, document_page_zoom_in, document_page_zoom_out, document_page_view_reset], menu_name='form_header')
register_links(DocumentPageTransformation, [document_page_transformation_edit, document_page_transformation_delete])
register_links('documents:document_page_transformation_list', [document_page_transformation_create], menu_name='sidebar')
register_links('documents:document_page_transformation_create', [document_page_transformation_create], menu_name='sidebar')
register_links(['documents:document_page_transformation_edit', 'documents:document_page_transformation_delete'], [document_page_transformation_create], menu_name='sidebar')

register_diagnostic('documents', _(u'Documents'), document_missing_list)
register_maintenance_links([document_clear_image_cache], namespace='documents', title=_(u'Documents'))
register_model_list_columns(Document, [
    {
        'name': _(u'Thumbnail'), 'attribute':
        encapsulate(lambda x: document_thumbnail(x, gallery_name='documents:document_list', title=getattr(x, 'filename', None), size=THUMBNAIL_SIZE))
    },
    {
        'name': _(u'Type'), 'attribute': 'document_type'
    }
])

register_top_menu(
    'documents',
    link={'famfam': 'page', 'text': _(u'Documents'), 'view': 'documents:document_list_recent'},
    children_path_regex=[
        r'^documents/[^t]', r'^metadata/[^s]', r'comments', r'tags/document', r'grouping/[^s]', r'history/list/for_object/documents',
    ],
    children_view_regex=[r'documents:document_acl', r'smart_link_instance'],
    children_views=['documents:document_folder_list', 'folders:folder_add_document', 'documents:document_index_list', 'documents:upload_version', ],
    position=1
)

register_links(Document, [document_view_simple], menu_name='form_header', position=0)
register_links(Document, [document_view_advanced], menu_name='form_header', position=1)
register_links(Document, [document_history_view], menu_name='form_header')
register_links(Document, [document_version_list], menu_name='form_header')

if (not validate_path(document_settings.CACHE_PATH)) or (not document_settings.CACHE_PATH):
    setattr(document_settings, 'CACHE_PATH', tempfile.mkdtemp())

register_setup(document_type_setup)

class_permissions(Document, [PERMISSION_DOCUMENT_DELETE,
                             PERMISSION_DOCUMENT_DOWNLOAD,
                             PERMISSION_DOCUMENT_EDIT,
                             PERMISSION_DOCUMENT_NEW_VERSION,
                             PERMISSION_DOCUMENT_PROPERTIES_EDIT,
                             PERMISSION_DOCUMENT_TRANSFORM,
                             PERMISSION_DOCUMENT_VERSION_REVERT,
                             PERMISSION_DOCUMENT_VIEW,
                             PERMISSION_HISTORY_VIEW])

document_search = SearchModel('documents', 'Document', permission=PERMISSION_DOCUMENT_VIEW, serializer=DocumentSerializer)

# TODO: move these to their respective apps
# Moving these to other apps cause an ImportError; circular import?
document_search.add_model_field('document_type__name', label=_(u'Document type'))
document_search.add_model_field('versions__mimetype', label=_(u'MIME type'))
document_search.add_model_field('versions__filename', label=_(u'Filename'))
document_search.add_model_field('metadata__metadata_type__name', label=_(u'Metadata type'))
document_search.add_model_field('metadata__value', label=_(u'Metadata value'))
document_search.add_model_field('versions__pages__content', label=_(u'Content'))
document_search.add_model_field('description', label=_(u'Description'))

namespace = StatisticNamespace(name='documents', label=_(u'Documents'))
namespace.add_statistic(DocumentStatistics(name='document_stats', label=_(u'Document tendencies')))
namespace.add_statistic(DocumentUsageStatistics(name='document_usage', label=_(u'Document usage')))

endpoint = APIEndPoint('documents')
endpoint.register_urls(api_urls)
endpoint.add_endpoint('document-list', _(u'Returns a list of all the documents.'))
endpoint.add_endpoint('documenttype-list', _(u'Returns a list of all the document types.'))
