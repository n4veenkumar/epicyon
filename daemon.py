__filename__ = "daemon.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.3.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Core"

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
import sys
import json
import time
import urllib.parse
import datetime
from socket import error as SocketError
import errno
from functools import partial
import pyqrcode
# for saving images
from hashlib import sha256
from hashlib import md5
from shutil import copyfile
from session import create_session
from webfinger import webfinger_meta
from webfinger import webfinger_node_info
from webfinger import webfinger_lookup
from webfinger import webfinger_update
from mastoapiv1 import masto_api_v1_response
from metadata import meta_data_node_info
from metadata import metadata_custom_emoji
from enigma import get_enigma_pub_key
from enigma import set_enigma_pub_key
from pgp import get_email_address
from pgp import set_email_address
from pgp import get_pgp_pub_key
from pgp import get_pgp_fingerprint
from pgp import set_pgp_pub_key
from pgp import set_pgp_fingerprint
from xmpp import get_xmpp_address
from xmpp import set_xmpp_address
from ssb import get_ssb_address
from ssb import set_ssb_address
from tox import get_tox_address
from tox import set_tox_address
from briar import get_briar_address
from briar import set_briar_address
from jami import get_jami_address
from jami import set_jami_address
from cwtch import get_cwtch_address
from cwtch import set_cwtch_address
from matrix import get_matrix_address
from matrix import set_matrix_address
from donate import get_donation_url
from donate import set_donation_url
from donate import get_website
from donate import set_website
from person import add_actor_update_timestamp
from person import set_person_notes
from person import get_default_person_context
from person import get_actor_update_json
from person import save_person_qrcode
from person import randomize_actor_images
from person import person_upgrade_actor
from person import activate_account
from person import deactivate_account
from person import register_account
from person import person_lookup
from person import person_box_json
from person import create_shared_inbox
from person import create_news_inbox
from person import suspend_account
from person import reenable_account
from person import remove_account
from person import can_remove_post
from person import person_snooze
from person import person_unsnooze
from posts import get_original_post_from_announce_url
from posts import save_post_to_box
from posts import get_instance_actor_key
from posts import remove_post_interactions
from posts import outbox_message_create_wrap
from posts import get_pinned_post_as_json
from posts import pin_post
from posts import json_pin_post
from posts import undo_pinned_post
from posts import is_moderator
from posts import create_question_post
from posts import create_public_post
from posts import create_blog_post
from posts import create_report_post
from posts import create_unlisted_post
from posts import create_followers_only_post
from posts import create_direct_message_post
from posts import populate_replies_json
from posts import add_to_field
from posts import expire_cache
from inbox import clear_queue_items
from inbox import inbox_permitted_message
from inbox import inbox_message_has_params
from inbox import run_inbox_queue
from inbox import run_inbox_queue_watchdog
from inbox import save_post_to_inbox_queue
from inbox import populate_replies
from follow import follower_approval_active
from follow import is_following_actor
from follow import get_following_feed
from follow import send_follow_request
from follow import unfollow_account
from follow import create_initial_last_seen
from skills import get_skills_from_list
from skills import no_of_actor_skills
from skills import actor_has_skill
from skills import actor_skill_value
from skills import set_actor_skill_level
from auth import record_login_failure
from auth import authorize
from auth import create_password
from auth import create_basic_auth_header
from auth import authorize_basic
from auth import store_basic_credentials
from threads import thread_with_trace
from threads import remove_dormant_threads
from media import process_meta_data
from media import convert_image_to_low_bandwidth
from media import replace_you_tube
from media import replace_twitter
from media import attach_media
from media import path_is_video
from media import path_is_audio
from blocking import get_cw_list_variable
from blocking import load_cw_lists
from blocking import update_blocked_cache
from blocking import mute_post
from blocking import unmute_post
from blocking import set_broch_mode
from blocking import broch_mode_is_active
from blocking import add_block
from blocking import remove_block
from blocking import add_global_block
from blocking import remove_global_block
from blocking import is_blocked_hashtag
from blocking import is_blocked_domain
from blocking import get_domain_blocklist
from roles import get_actor_roles_list
from roles import set_role
from roles import clear_moderator_status
from roles import clear_editor_status
from roles import clear_counselor_status
from roles import clear_artist_status
from blog import path_contains_blog_link
from blog import html_blog_page_rss2
from blog import html_blog_page_rss3
from blog import html_blog_view
from blog import html_blog_page
from blog import html_blog_post
from blog import html_edit_blog
from blog import get_blog_address
from webapp_podcast import html_podcast_episode
from webapp_theme_designer import html_theme_designer
from webapp_minimalbutton import set_minimal
from webapp_minimalbutton import is_minimal
from webapp_utils import get_avatar_image_url
from webapp_utils import html_hashtag_blocked
from webapp_utils import html_following_list
from webapp_utils import set_blog_address
from webapp_utils import html_show_share
from webapp_calendar import html_calendar_delete_confirm
from webapp_calendar import html_calendar
from webapp_about import html_about
from webapp_accesskeys import html_access_keys
from webapp_accesskeys import load_access_keys_for_accounts
from webapp_confirm import html_confirm_delete
from webapp_confirm import html_confirm_remove_shared_item
from webapp_confirm import html_confirm_unblock
from webapp_person_options import html_person_options
from webapp_timeline import html_shares
from webapp_timeline import html_wanted
from webapp_timeline import html_inbox
from webapp_timeline import html_bookmarks
from webapp_timeline import html_inbox_dms
from webapp_timeline import html_inbox_replies
from webapp_timeline import html_inbox_media
from webapp_timeline import html_inbox_blogs
from webapp_timeline import html_inbox_news
from webapp_timeline import html_inbox_features
from webapp_timeline import html_outbox
from webapp_media import load_peertube_instances
from webapp_moderation import html_account_info
from webapp_moderation import html_moderation
from webapp_moderation import html_moderation_info
from webapp_create_post import html_new_post
from webapp_login import html_login
from webapp_login import html_get_login_credentials
from webapp_suspended import html_suspended
from webapp_tos import html_terms_of_service
from webapp_confirm import html_confirm_follow
from webapp_confirm import html_confirm_unfollow
from webapp_post import html_emoji_reaction_picker
from webapp_post import html_post_replies
from webapp_post import html_individual_post
from webapp_post import individual_post_as_html
from webapp_profile import html_edit_profile
from webapp_profile import html_profile_after_search
from webapp_profile import html_profile
from webapp_column_left import html_links_mobile
from webapp_column_left import html_edit_links
from webapp_column_right import html_newswire_mobile
from webapp_column_right import html_edit_newswire
from webapp_column_right import html_citations
from webapp_column_right import html_edit_news_post
from webapp_search import html_skills_search
from webapp_search import html_history_search
from webapp_search import html_hashtag_search
from webapp_search import rss_hashtag_search
from webapp_search import html_search_emoji
from webapp_search import html_search_shared_items
from webapp_search import html_search_emoji_text_entry
from webapp_search import html_search
from webapp_hashtagswarm import get_hashtag_categories_feed
from webapp_hashtagswarm import html_search_hashtag_category
from webapp_welcome import welcome_screen_is_complete
from webapp_welcome import html_welcome_screen
from webapp_welcome import is_welcome_screen_complete
from webapp_welcome_profile import html_welcome_profile
from webapp_welcome_final import html_welcome_final
from shares import merge_shared_item_tokens
from shares import run_federated_shares_daemon
from shares import run_federated_shares_watchdog
from shares import update_shared_item_federation_token
from shares import create_shared_item_federation_token
from shares import authorize_shared_items
from shares import generate_shared_item_federation_tokens
from shares import get_shares_feed_for_person
from shares import add_share
from shares import remove_shared_item
from shares import expire_shares
from shares import shares_catalog_endpoint
from shares import shares_catalog_account_endpoint
from shares import shares_catalog_csv_endpoint
from categories import set_hashtag_category
from categories import update_hashtag_categories
from languages import get_actor_languages
from languages import set_actor_languages
from languages import get_understood_languages
from like import update_likes_collection
from reaction import update_reaction_collection
from utils import local_network_host
from utils import undo_reaction_collection_entry
from utils import get_new_post_endpoints
from utils import has_actor
from utils import set_reply_interval_hours
from utils import can_reply_to
from utils import is_dm
from utils import replace_users_with_at
from utils import local_actor_url
from utils import is_float
from utils import valid_password
from utils import remove_line_endings
from utils import get_base_content_from_post
from utils import acct_dir
from utils import get_image_extension_from_mime_type
from utils import get_image_mime_type
from utils import has_object_dict
from utils import user_agent_domain
from utils import is_local_network_address
from utils import permitted_dir
from utils import is_account_dir
from utils import get_occupation_skills
from utils import get_occupation_name
from utils import set_occupation_name
from utils import load_translations_from_file
from utils import get_local_network_addresses
from utils import decoded_host
from utils import is_public_post
from utils import get_locked_account
from utils import has_users_path
from utils import get_full_domain
from utils import remove_html
from utils import is_editor
from utils import is_artist
from utils import get_image_extensions
from utils import media_file_mime_type
from utils import get_css
from utils import first_paragraph_from_string
from utils import clear_from_post_caches
from utils import contains_invalid_chars
from utils import is_system_account
from utils import set_config_param
from utils import get_config_param
from utils import remove_id_ending
from utils import undo_likes_collection_entry
from utils import delete_post
from utils import is_blog_post
from utils import remove_avatar_from_cache
from utils import locate_post
from utils import get_cached_post_filename
from utils import remove_post_from_cache
from utils import get_nickname_from_actor
from utils import get_domain_from_actor
from utils import get_status_number
from utils import url_permitted
from utils import load_json
from utils import save_json
from utils import is_suspended
from utils import dangerous_markup
from utils import refresh_newswire
from utils import is_image_file
from utils import has_group_type
from manualapprove import manual_deny_follow_request_thread
from manualapprove import manual_approve_follow_request_thread
from announce import create_announce
from content import contains_invalid_local_links
from content import get_price_from_string
from content import replace_emoji_from_tags
from content import add_html_tags
from content import extract_media_in_form_post
from content import save_media_in_form_post
from content import extract_text_fields_in_post
from cache import check_for_changed_actor
from cache import store_person_in_cache
from cache import get_person_from_cache
from cache import get_person_pub_key
from httpsig import verify_post_headers
from theme import reset_theme_designer_settings
from theme import set_theme_from_designer
from theme import scan_themes_for_scripts
from theme import import_theme
from theme import export_theme
from theme import is_news_theme_name
from theme import get_text_mode_banner
from theme import set_news_avatar
from theme import set_theme
from theme import get_theme
from theme import enable_grayscale
from theme import disable_grayscale
from schedule import run_post_schedule
from schedule import run_post_schedule_watchdog
from schedule import remove_scheduled_posts
from outbox import post_message_to_outbox
from happening import remove_calendar_event
from bookmarks import bookmark_post
from bookmarks import undo_bookmark_post
from petnames import set_pet_name
from followingCalendar import add_person_to_calendar
from followingCalendar import remove_person_from_calendar
from notifyOnPost import add_notify_on_post
from notifyOnPost import remove_notify_on_post
from devices import e2e_edevices_collection
from devices import e2e_evalid_device
from devices import e2e_eadd_device
from newswire import get_rs_sfrom_dict
from newswire import rss2header
from newswire import rss2footer
from newswire import load_hashtag_categories
from newsdaemon import run_newswire_watchdog
from newsdaemon import run_newswire_daemon
from filters import is_filtered
from filters import add_global_filter
from filters import remove_global_filter
from context import has_valid_context
from context import get_individual_post_context
from speaker import get_ssm_lbox
from city import get_spoofed_city
from fitnessFunctions import fitness_performance
from fitnessFunctions import fitness_thread
from fitnessFunctions import sorted_watch_points
from fitnessFunctions import html_watch_points_graph
from siteactive import site_is_active
import os


# maximum number of posts to list in outbox feed
MAX_POSTS_IN_FEED = 12

# maximum number of posts in a hashtag feed
MAX_POSTS_IN_HASHTAG_FEED = 6

# reduced posts for media feed because it can take a while
MAX_POSTS_IN_MEDIA_FEED = 6

# Blogs can be longer, so don't show many per page
MAX_POSTS_IN_BLOGS_FEED = 4

MAX_POSTS_IN_NEWS_FEED = 10

# Maximum number of entries in returned rss.xml
MAX_POSTS_IN_RSS_FEED = 10

# number of follows/followers per page
FOLLOWS_PER_PAGE = 6

# number of item shares per page
SHARES_PER_PAGE = 12


def save_domain_qrcode(base_dir: str, http_prefix: str,
                       domain_full: str, scale=6) -> None:
    """Saves a qrcode image for the domain name
    This helps to transfer onion or i2p domains to a mobile device
    """
    qrcode_filename = base_dir + '/accounts/qrcode.png'
    url = pyqrcode.create(http_prefix + '://' + domain_full)
    url.png(qrcode_filename, scale)


class PubServer(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _update_known_crawlers(self, ua_str: str) -> None:
        """Updates a dictionary of known crawlers accessing nodeinfo
        or the masto API
        """
        if not ua_str:
            return

        curr_time = int(time.time())
        if self.server.known_crawlers.get(ua_str):
            self.server.known_crawlers[ua_str]['hits'] += 1
            self.server.known_crawlers[ua_str]['lastseen'] = curr_time
        else:
            self.server.known_crawlers[ua_str] = {
                "lastseen": curr_time,
                "hits": 1
            }

        if curr_time - self.server.last_known_crawler >= 30:
            # remove any old observations
            remove_crawlers = []
            for uagent, item in self.server.known_crawlers.items():
                if curr_time - item['lastseen'] >= 60 * 60 * 24 * 30:
                    remove_crawlers.append(uagent)
            for uagent in remove_crawlers:
                del self.server.known_crawlers[uagent]
            # save the list of crawlers
            save_json(self.server.known_crawlers,
                      self.server.base_dir + '/accounts/knownCrawlers.json')
        self.server.last_known_crawler = curr_time

    def _get_instance_url(self, calling_domain: str) -> str:
        """Returns the URL for this instance
        """
        if calling_domain.endswith('.onion') and \
           self.server.onion_domain:
            instance_url = 'http://' + self.server.onion_domain
        elif (calling_domain.endswith('.i2p') and
              self.server.i2p_domain):
            instance_url = 'http://' + self.server.i2p_domain
        else:
            instance_url = \
                self.server.http_prefix + '://' + self.server.domain_full
        return instance_url

    def _getheader_signature_input(self):
        """There are different versions of http signatures with
        different header styles
        """
        if self.headers.get('Signature-Input'):
            # https://tools.ietf.org/html/
            # draft-ietf-httpbis-message-signatures-01
            return self.headers['Signature-Input']
        if self.headers.get('signature-input'):
            return self.headers['signature-input']
        if self.headers.get('signature'):
            # Ye olde Masto http sig
            return self.headers['signature']
        return None

    def handle_error(self, request, client_address):
        print('ERROR: http server error: ' + str(request) + ', ' +
              str(client_address))
        pass

    def _send_reply_to_question(self, nickname: str, message_id: str,
                                answer: str) -> None:
        """Sends a reply to a question
        """
        votes_filename = \
            acct_dir(self.server.base_dir, nickname, self.server.domain) + \
            '/questions.txt'

        if os.path.isfile(votes_filename):
            # have we already voted on this?
            if message_id in open(votes_filename).read():
                print('Already voted on message ' + message_id)
                return

        print('Voting on message ' + message_id)
        print('Vote for: ' + answer)
        comments_enabled = True
        attach_image_filename = None
        media_type = None
        image_description = None
        in_reply_to = message_id
        in_reply_to_atom_uri = message_id
        subject = None
        schedule_post = False
        event_date = None
        event_time = None
        location = None
        conversation_id = None
        city = get_spoofed_city(self.server.city,
                                self.server.base_dir,
                                nickname, self.server.domain)
        languages_understood = \
            get_understood_languages(self.server.base_dir,
                                     self.server.http_prefix,
                                     nickname,
                                     self.server.domain_full,
                                     self.server.person_cache)

        message_json = \
            create_public_post(self.server.base_dir,
                               nickname,
                               self.server.domain, self.server.port,
                               self.server.http_prefix,
                               answer, False, False, False,
                               comments_enabled,
                               attach_image_filename, media_type,
                               image_description, city,
                               in_reply_to,
                               in_reply_to_atom_uri,
                               subject,
                               schedule_post,
                               event_date,
                               event_time,
                               location, False,
                               self.server.system_language,
                               conversation_id,
                               self.server.low_bandwidth,
                               self.server.content_license_url,
                               languages_understood)
        if message_json:
            # name field contains the answer
            message_json['object']['name'] = answer
            if self._post_to_outbox(message_json,
                                    self.server.project_version, nickname):
                post_filename = \
                    locate_post(self.server.base_dir, nickname,
                                self.server.domain, message_id)
                if post_filename:
                    post_json_object = load_json(post_filename)
                    if post_json_object:
                        populate_replies(self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain_full,
                                         post_json_object,
                                         self.server.max_replies,
                                         self.server.debug)
                        # record the vote
                        try:
                            with open(votes_filename, 'a+') as votes_file:
                                votes_file.write(message_id + '\n')
                        except OSError:
                            print('EX: unable to write vote ' +
                                  votes_filename)

                        # ensure that the cached post is removed if it exists,
                        # so that it then will be recreated
                        cached_post_filename = \
                            get_cached_post_filename(self.server.base_dir,
                                                     nickname,
                                                     self.server.domain,
                                                     post_json_object)
                        if cached_post_filename:
                            if os.path.isfile(cached_post_filename):
                                try:
                                    os.remove(cached_post_filename)
                                except OSError:
                                    print('EX: _send_reply_to_question ' +
                                          'unable to delete ' +
                                          cached_post_filename)
                        # remove from memory cache
                        remove_post_from_cache(post_json_object,
                                               self.server.recent_posts_cache)
            else:
                print('ERROR: unable to post vote to outbox')
        else:
            print('ERROR: unable to create vote')

    def _blocked_user_agent(self, calling_domain: str, agent_str: str) -> bool:
        """Should a GET or POST be blocked based upon its user agent?
        """
        if not agent_str:
            return False

        agent_str_lower = agent_str.lower()
        default_agent_blocks = [
            'fedilist'
        ]
        for ua_block in default_agent_blocks:
            if ua_block in agent_str_lower:
                print('Blocked User agent: ' + ua_block)
                return True

        agent_domain = None

        if agent_str:
            # is this a web crawler? If so the block it
            if 'bot/' in agent_str_lower or 'bot-' in agent_str_lower:
                if self.server.news_instance:
                    return False
                print('Blocked Crawler: ' + agent_str)
                return True
            # get domain name from User-Agent
            agent_domain = user_agent_domain(agent_str, self.server.debug)
        else:
            # no User-Agent header is present
            return True

        # is the User-Agent type blocked? eg. "Mastodon"
        if self.server.user_agents_blocked:
            blocked_ua = False
            for agent_name in self.server.user_agents_blocked:
                if agent_name in agent_str:
                    blocked_ua = True
                    break
            if blocked_ua:
                return True

        if not agent_domain:
            return False

        # is the User-Agent domain blocked
        blocked_ua = False
        if not agent_domain.startswith(calling_domain):
            self.server.blocked_cache_last_updated = \
                update_blocked_cache(self.server.base_dir,
                                     self.server.blocked_cache,
                                     self.server.blocked_cache_last_updated,
                                     self.server.blocked_cache_update_secs)

            blocked_ua = is_blocked_domain(self.server.base_dir, agent_domain,
                                           self.server.blocked_cache)
            # if self.server.debug:
            if blocked_ua:
                print('Blocked User agent: ' + agent_domain)
        return blocked_ua

    def _request_csv(self) -> bool:
        """Should a csv response be given?
        """
        if not self.headers.get('Accept'):
            return False
        accept_str = self.headers['Accept']
        if 'text/csv' in accept_str:
            return True
        return False

    def _request_http(self) -> bool:
        """Should a http response be given?
        """
        if not self.headers.get('Accept'):
            return False
        accept_str = self.headers['Accept']
        if self.server.debug:
            print('ACCEPT: ' + accept_str)
        if 'application/ssml' in accept_str:
            if 'text/html' not in accept_str:
                return False
        if 'image/' in accept_str:
            if 'text/html' not in accept_str:
                return False
        if 'video/' in accept_str:
            if 'text/html' not in accept_str:
                return False
        if 'audio/' in accept_str:
            if 'text/html' not in accept_str:
                return False
        if accept_str.startswith('*'):
            if self.headers.get('User-Agent'):
                if 'ELinks' in self.headers['User-Agent'] or \
                   'Lynx' in self.headers['User-Agent']:
                    return True
            return False
        if 'json' in accept_str:
            return False
        return True

    def _signed_ge_tkey_id(self) -> str:
        """Returns the actor from the signed GET key_id
        """
        signature = None
        if self.headers.get('signature'):
            signature = self.headers['signature']
        elif self.headers.get('Signature'):
            signature = self.headers['Signature']

        # check that the headers are signed
        if not signature:
            if self.server.debug:
                print('AUTH: secure mode actor, ' +
                      'GET has no signature in headers')
            return None

        # get the key_id, which is typically the instance actor
        key_id = None
        signature_params = signature.split(',')
        for signature_item in signature_params:
            if signature_item.startswith('keyId='):
                if '"' in signature_item:
                    key_id = signature_item.split('"')[1]
                    # remove #main-key
                    if '#' in key_id:
                        key_id = key_id.split('#')[0]
                    return key_id
        return None

    def _establish_session(self, calling_function: str) -> bool:
        """Recreates session if needed
        """
        if self.server.session:
            return True
        print('DEBUG: creating new session during ' + calling_function)
        self.server.session = create_session(self.server.proxy_type)
        if self.server.session:
            return True
        print('ERROR: GET failed to create session during ' +
              calling_function)
        return False

    def _secure_mode(self, force: bool = False) -> bool:
        """http authentication of GET requests for json
        """
        if not self.server.secure_mode and not force:
            return True

        key_id = self._signed_ge_tkey_id()
        if not key_id:
            if self.server.debug:
                print('AUTH: secure mode, ' +
                      'failed to obtain key_id from signature')
            return False

        # is the key_id (actor) valid?
        if not url_permitted(key_id, self.server.federation_list):
            if self.server.debug:
                print('AUTH: Secure mode GET request not permitted: ' + key_id)
            return False

        if not self._establish_session("secure mode"):
            return False

        # obtain the public key
        pub_key = \
            get_person_pub_key(self.server.base_dir,
                               self.server.session, key_id,
                               self.server.person_cache, self.server.debug,
                               self.server.project_version,
                               self.server.http_prefix,
                               self.server.domain, self.server.onion_domain,
                               self.server.signing_priv_key_pem)
        if not pub_key:
            if self.server.debug:
                print('AUTH: secure mode failed to ' +
                      'obtain public key for ' + key_id)
            return False

        # verify the GET request without any digest
        if verify_post_headers(self.server.http_prefix,
                               self.server.domain_full,
                               pub_key, self.headers,
                               self.path, True, None, '', self.server.debug):
            return True

        if self.server.debug:
            print('AUTH: secure mode authorization failed for ' + key_id)
        return False

    def _login_headers(self, file_format: str, length: int,
                       calling_domain: str) -> None:
        self.send_response(200)
        self.send_header('Content-type', file_format)
        self.send_header('Content-Length', str(length))
        self.send_header('Host', calling_domain)
        self.send_header('WWW-Authenticate',
                         'title="Login to Epicyon", Basic realm="epicyon"')
        self.end_headers()

    def _logout_headers(self, file_format: str, length: int,
                        calling_domain: str) -> None:
        self.send_response(200)
        self.send_header('Content-type', file_format)
        self.send_header('Content-Length', str(length))
        self.send_header('Set-Cookie', 'epicyon=; SameSite=Strict')
        self.send_header('Host', calling_domain)
        self.send_header('WWW-Authenticate',
                         'title="Login to Epicyon", Basic realm="epicyon"')
        self.end_headers()

    def _quoted_redirect(self, redirect: str) -> str:
        """hashtag screen urls sometimes contain non-ascii characters which
        need to be url encoded
        """
        if '/tags/' not in redirect:
            return redirect
        last_str = redirect.split('/')[-1]
        return redirect.replace('/' + last_str, '/' +
                                urllib.parse.quote_plus(last_str))

    def _logout_redirect(self, redirect: str, cookie: str,
                         calling_domain: str) -> None:
        if '://' not in redirect:
            print('REDIRECT ERROR: redirect is not an absolute url ' +
                  redirect)

        self.send_response(303)
        self.send_header('Set-Cookie', 'epicyon=; SameSite=Strict')
        self.send_header('Location', self._quoted_redirect(redirect))
        self.send_header('Host', calling_domain)
        self.send_header('X-AP-Instance-ID', self.server.instance_id)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _set_headers_base(self, file_format: str, length: int, cookie: str,
                          calling_domain: str, permissive: bool) -> None:
        self.send_response(200)
        self.send_header('Content-type', file_format)
        if 'image/' in file_format or \
           'audio/' in file_format or \
           'video/' in file_format:
            cache_control = 'public, max-age=84600, immutable'
            self.send_header('Cache-Control', cache_control)
        else:
            self.send_header('Cache-Control', 'public')
        self.send_header('Origin', self.server.domain_full)
        if length > -1:
            self.send_header('Content-Length', str(length))
        if calling_domain:
            self.send_header('Host', calling_domain)
        if permissive:
            self.send_header('Access-Control-Allow-Origin', '*')
            return
        self.send_header('X-AP-Instance-ID', self.server.instance_id)
        self.send_header('X-Clacks-Overhead', 'GNU Natalie Nguyen')
        if cookie:
            cookie_str = cookie
            if 'HttpOnly;' not in cookie_str:
                if self.server.http_prefix == 'https':
                    cookie_str += '; Secure'
                cookie_str += '; HttpOnly; SameSite=Strict'
            self.send_header('Cookie', cookie_str)

    def _set_headers(self, file_format: str, length: int, cookie: str,
                     calling_domain: str, permissive: bool) -> None:
        self._set_headers_base(file_format, length, cookie, calling_domain,
                               permissive)
        self.end_headers()

    def _set_headers_head(self, file_format: str, length: int, etag: str,
                          calling_domain: str, permissive: bool) -> None:
        self._set_headers_base(file_format, length, None, calling_domain,
                               permissive)
        if etag:
            self.send_header('ETag', '"' + etag + '"')
        self.end_headers()

    def _set_headers_etag(self, media_filename: str, file_format: str,
                          data, cookie: str, calling_domain: str,
                          permissive: bool, last_modified: str) -> None:
        datalen = len(data)
        self._set_headers_base(file_format, datalen, cookie, calling_domain,
                               permissive)
        etag = None
        if os.path.isfile(media_filename + '.etag'):
            try:
                with open(media_filename + '.etag', 'r') as efile:
                    etag = efile.read()
            except OSError:
                print('EX: _set_headers_etag ' +
                      'unable to read ' + media_filename + '.etag')
        if not etag:
            etag = md5(data).hexdigest()  # nosec
            try:
                with open(media_filename + '.etag', 'w+') as efile:
                    efile.write(etag)
            except OSError:
                print('EX: _set_headers_etag ' +
                      'unable to write ' + media_filename + '.etag')
        # if etag:
        #     self.send_header('ETag', '"' + etag + '"')
        if last_modified:
            self.send_header('last-modified', last_modified)
        self.end_headers()

    def _etag_exists(self, media_filename: str) -> bool:
        """Does an etag header exist for the given file?
        """
        etag_header = 'If-None-Match'
        if not self.headers.get(etag_header):
            etag_header = 'if-none-match'
            if not self.headers.get(etag_header):
                etag_header = 'If-none-match'

        if self.headers.get(etag_header):
            old_etag = self.headers[etag_header].replace('"', '')
            if os.path.isfile(media_filename + '.etag'):
                # load the etag from file
                curr_etag = ''
                try:
                    with open(media_filename + '.etag', 'r') as efile:
                        curr_etag = efile.read()
                except OSError:
                    print('EX: _etag_exists unable to read ' +
                          str(media_filename))
                if curr_etag and old_etag == curr_etag:
                    # The file has not changed
                    return True
        return False

    def _redirect_headers(self, redirect: str, cookie: str,
                          calling_domain: str) -> None:
        if '://' not in redirect:
            print('REDIRECT ERROR: redirect is not an absolute url ' +
                  redirect)

        self.send_response(303)

        if cookie:
            cookie_str = cookie.replace('SET:', '').strip()
            if 'HttpOnly;' not in cookie_str:
                if self.server.http_prefix == 'https':
                    cookie_str += '; Secure'
                cookie_str += '; HttpOnly; SameSite=Strict'
            if not cookie.startswith('SET:'):
                self.send_header('Cookie', cookie_str)
            else:
                self.send_header('Set-Cookie', cookie_str)
        self.send_header('Location', self._quoted_redirect(redirect))
        self.send_header('Host', calling_domain)
        self.send_header('X-AP-Instance-ID', self.server.instance_id)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _http_return_code(self, http_code: int, http_description: str,
                          long_description: str) -> None:
        msg = \
            '<html><head><title>' + str(http_code) + '</title></head>' \
            '<body bgcolor="linen" text="black">' \
            '<div style="font-size: 400px; ' \
            'text-align: center;">' + str(http_code) + '</div>' \
            '<div style="font-size: 128px; ' \
            'text-align: center; font-variant: ' \
            'small-caps;"><p role="alert">' + http_description + '</p></div>' \
            '<div style="text-align: center;">' + long_description + '</div>' \
            '</body></html>'
        msg = msg.encode('utf-8')
        self.send_response(http_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        msg_len_str = str(len(msg))
        self.send_header('Content-Length', msg_len_str)
        self.end_headers()
        if not self._write(msg):
            print('Error when showing ' + str(http_code))

    def _200(self) -> None:
        if self.server.translate:
            ok_str = self.server.translate['This is nothing ' +
                                           'less than an utter triumph']
            self._http_return_code(200, self.server.translate['Ok'], ok_str)
        else:
            self._http_return_code(200, 'Ok',
                                   'This is nothing less ' +
                                   'than an utter triumph')

    def _403(self) -> None:
        if self.server.translate:
            self._http_return_code(403, self.server.translate['Forbidden'],
                                   self.server.translate["You're not allowed"])
        else:
            self._http_return_code(403, 'Forbidden',
                                   "You're not allowed")

    def _404(self) -> None:
        if self.server.translate:
            self._http_return_code(404, self.server.translate['Not Found'],
                                   self.server.translate['These are not the ' +
                                                         'droids you are ' +
                                                         'looking for'])
        else:
            self._http_return_code(404, 'Not Found',
                                   'These are not the ' +
                                   'droids you are ' +
                                   'looking for')

    def _304(self) -> None:
        if self.server.translate:
            self._http_return_code(304, self.server.translate['Not changed'],
                                   self.server.translate['The contents of ' +
                                                         'your local cache ' +
                                                         'are up to date'])
        else:
            self._http_return_code(304, 'Not changed',
                                   'The contents of ' +
                                   'your local cache ' +
                                   'are up to date')

    def _400(self) -> None:
        if self.server.translate:
            self._http_return_code(400, self.server.translate['Bad Request'],
                                   self.server.translate['Better luck ' +
                                                         'next time'])
        else:
            self._http_return_code(400, 'Bad Request',
                                   'Better luck next time')

    def _503(self) -> None:
        if self.server.translate:
            busy_str = \
                self.server.translate['The server is busy. ' +
                                      'Please try again later']
            self._http_return_code(503, self.server.translate['Unavailable'],
                                   busy_str)
        else:
            self._http_return_code(503, 'Unavailable',
                                   'The server is busy. Please try again ' +
                                   'later')

    def _write(self, msg) -> bool:
        tries = 0
        while tries < 5:
            try:
                self.wfile.write(msg)
                return True
            except BrokenPipeError as ex:
                if self.server.debug:
                    print('EX: _write error ' + str(tries) + ' ' + str(ex))
                break
            except BaseException as ex:
                print('EX: _write error ' + str(tries) + ' ' + str(ex))
                time.sleep(0.5)
            tries += 1
        return False

    def _has_accept(self, calling_domain: str) -> bool:
        """Do the http headers have an Accept field?
        """
        if not self.headers.get('Accept'):
            if self.headers.get('accept'):
                print('Upper case Accept')
                self.headers['Accept'] = self.headers['accept']

        if self.headers.get('Accept') or calling_domain.endswith('.b32.i2p'):
            if not self.headers.get('Accept'):
                self.headers['Accept'] = \
                    'text/html,application/xhtml+xml,' \
                    'application/xml;q=0.9,image/webp,*/*;q=0.8'
            return True
        return False

    def _masto_api_v1(self, path: str, calling_domain: str,
                      ua_str: str,
                      authorized: bool,
                      http_prefix: str,
                      base_dir: str, nickname: str, domain: str,
                      domain_full: str,
                      onion_domain: str, i2p_domain: str,
                      translate: {},
                      registration: bool,
                      system_language: str,
                      project_version: str,
                      custom_emoji: [],
                      show_node_info_accounts: bool) -> bool:
        """This is a vestigil mastodon API for the purpose
        of returning an empty result to sites like
        https://mastopeek.app-dist.eu
        """
        if not path.startswith('/api/v1/'):
            return False
        print('mastodon api v1: ' + path)
        print('mastodon api v1: authorized ' + str(authorized))
        print('mastodon api v1: nickname ' + str(nickname))
        self._update_known_crawlers(ua_str)

        broch_mode = broch_mode_is_active(base_dir)
        send_json, send_json_str = \
            masto_api_v1_response(path,
                                  calling_domain,
                                  ua_str,
                                  authorized,
                                  http_prefix,
                                  base_dir,
                                  nickname, domain,
                                  domain_full,
                                  onion_domain,
                                  i2p_domain,
                                  translate,
                                  registration,
                                  system_language,
                                  project_version,
                                  custom_emoji,
                                  show_node_info_accounts,
                                  broch_mode)

        if send_json is not None:
            msg = json.dumps(send_json).encode('utf-8')
            msglen = len(msg)
            if self._has_accept(calling_domain):
                if 'application/ld+json' in self.headers['Accept']:
                    self._set_headers('application/ld+json', msglen,
                                      None, calling_domain, True)
                else:
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, True)
            else:
                self._set_headers('application/ld+json', msglen,
                                  None, calling_domain, True)
            self._write(msg)
            if send_json_str:
                print(send_json_str)
            return True

        # no api endpoints were matched
        self._404()
        return True

    def _masto_api(self, path: str, calling_domain: str,
                   ua_str: str,
                   authorized: bool, http_prefix: str,
                   base_dir: str, nickname: str, domain: str,
                   domain_full: str,
                   onion_domain: str, i2p_domain: str,
                   translate: {},
                   registration: bool,
                   system_language: str,
                   project_version: str,
                   custom_emoji: [],
                   show_node_info_accounts: bool) -> bool:
        return self._masto_api_v1(path, calling_domain, ua_str, authorized,
                                  http_prefix, base_dir, nickname, domain,
                                  domain_full, onion_domain, i2p_domain,
                                  translate, registration, system_language,
                                  project_version, custom_emoji,
                                  show_node_info_accounts)

    def _nodeinfo(self, ua_str: str, calling_domain: str,
                  referer_domain: str,
                  httpPrefix: str, calling_site_timeout: int,
                  debug: bool) -> bool:
        if self.path.startswith('/nodeinfo/1.0'):
            self._400()
            return True
        if not self.path.startswith('/nodeinfo/2.0'):
            return False
        if not referer_domain:
            if not debug and not self.server.unit_test:
                print('nodeinfo request has no referer domain ' + str(ua_str))
                self._400()
                return True
        if referer_domain == self.server.domain_full:
            print('nodeinfo request from self')
            self._400()
            return True
        if self.server.nodeinfo_is_active:
            print('nodeinfo is busy during request from ' + referer_domain)
            self._503()
            return True
        self.server.nodeinfo_is_active = True
        # is this a real website making the call ?
        if not debug and not self.server.unit_test and referer_domain:
            # Does calling_domain look like a domain?
            if ' ' in referer_domain or \
               ';' in referer_domain or \
               '.' not in referer_domain:
                print('nodeinfo referer domain does not look like a domain ' +
                      referer_domain)
                self._400()
                self.server.nodeinfo_is_active = False
                return True
            if not self.server.allow_local_network_access:
                if local_network_host(referer_domain):
                    print('nodeinfo referer domain is from the ' +
                          'local network ' + referer_domain)
                    self._400()
                    self.server.nodeinfo_is_active = False
                    return True

            referer_url = httpPrefix + '://' + referer_domain
            if referer_domain + '/' in ua_str:
                referer_url = referer_url + ua_str.split(referer_domain)[1]
                if ' ' in referer_url:
                    referer_url = referer_url.split(' ')[0]
                if ';' in referer_url:
                    referer_url = referer_url.split(';')[0]
                if ')' in referer_url:
                    referer_url = referer_url.split(')')[0]
            if not site_is_active(referer_url, calling_site_timeout):
                print('nodeinfo referer url is not active ' +
                      referer_url)
                self._400()
                self.server.nodeinfo_is_active = False
                return True
        if self.server.debug:
            print('DEBUG: nodeinfo ' + self.path)
        self._update_known_crawlers(ua_str)

        # If we are in broch mode then don't show potentially
        # sensitive metadata.
        # For example, if this or allied instances are being attacked
        # then numbers of accounts may be changing as people
        # migrate, and that information may be useful to an adversary
        broch_mode = broch_mode_is_active(self.server.base_dir)

        node_info_version = self.server.project_version
        if not self.server.show_node_info_version or broch_mode:
            node_info_version = '0.0.0'

        show_node_info_accounts = self.server.show_node_info_accounts
        if broch_mode:
            show_node_info_accounts = False

        instance_url = self._get_instance_url(calling_domain)
        about_url = instance_url + '/about'
        terms_of_service_url = instance_url + '/terms'
        info = meta_data_node_info(self.server.base_dir,
                                   about_url, terms_of_service_url,
                                   self.server.registration,
                                   node_info_version,
                                   show_node_info_accounts)
        if info:
            msg = json.dumps(info).encode('utf-8')
            msglen = len(msg)
            if self._has_accept(calling_domain):
                if 'application/ld+json' in self.headers['Accept']:
                    self._set_headers('application/ld+json', msglen,
                                      None, calling_domain, True)
                else:
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, True)
            else:
                self._set_headers('application/ld+json', msglen,
                                  None, calling_domain, True)
            self._write(msg)
            print('nodeinfo sent to ' + referer_domain)
            self.server.nodeinfo_is_active = False
            return True
        self._404()
        self.server.nodeinfo_is_active = False
        return True

    def _webfinger(self, calling_domain: str) -> bool:
        if not self.path.startswith('/.well-known'):
            return False
        if self.server.debug:
            print('DEBUG: WEBFINGER well-known')

        if self.server.debug:
            print('DEBUG: WEBFINGER host-meta')
        if self.path.startswith('/.well-known/host-meta'):
            if calling_domain.endswith('.onion') and \
               self.server.onion_domain:
                wf_result = \
                    webfinger_meta('http', self.server.onion_domain)
            elif (calling_domain.endswith('.i2p') and
                  self.server.i2p_domain):
                wf_result = \
                    webfinger_meta('http', self.server.i2p_domain)
            else:
                wf_result = \
                    webfinger_meta(self.server.http_prefix,
                                   self.server.domain_full)
            if wf_result:
                msg = wf_result.encode('utf-8')
                msglen = len(msg)
                self._set_headers('application/xrd+xml', msglen,
                                  None, calling_domain, True)
                self._write(msg)
                return True
            self._404()
            return True
        if self.path.startswith('/api/statusnet') or \
           self.path.startswith('/api/gnusocial') or \
           self.path.startswith('/siteinfo') or \
           self.path.startswith('/poco') or \
           self.path.startswith('/friendi'):
            self._404()
            return True
        if self.path.startswith('/.well-known/nodeinfo') or \
           self.path.startswith('/.well-known/x-nodeinfo'):
            if calling_domain.endswith('.onion') and \
               self.server.onion_domain:
                wf_result = \
                    webfinger_node_info('http', self.server.onion_domain)
            elif (calling_domain.endswith('.i2p') and
                  self.server.i2p_domain):
                wf_result = \
                    webfinger_node_info('http', self.server.i2p_domain)
            else:
                wf_result = \
                    webfinger_node_info(self.server.http_prefix,
                                        self.server.domain_full)
            if wf_result:
                msg = json.dumps(wf_result).encode('utf-8')
                msglen = len(msg)
                if self._has_accept(calling_domain):
                    if 'application/ld+json' in self.headers['Accept']:
                        self._set_headers('application/ld+json', msglen,
                                          None, calling_domain, True)
                    else:
                        self._set_headers('application/json', msglen,
                                          None, calling_domain, True)
                else:
                    self._set_headers('application/ld+json', msglen,
                                      None, calling_domain, True)
                self._write(msg)
                return True
            self._404()
            return True

        if self.server.debug:
            print('DEBUG: WEBFINGER lookup ' + self.path + ' ' +
                  str(self.server.base_dir))
        wf_result = \
            webfinger_lookup(self.path, self.server.base_dir,
                             self.server.domain, self.server.onion_domain,
                             self.server.port, self.server.debug)
        if wf_result:
            msg = json.dumps(wf_result).encode('utf-8')
            msglen = len(msg)
            self._set_headers('application/jrd+json', msglen,
                              None, calling_domain, True)
            self._write(msg)
        else:
            if self.server.debug:
                print('DEBUG: WEBFINGER lookup 404 ' + self.path)
            self._404()
        return True

    def _post_to_outbox(self, message_json: {}, version: str,
                        post_to_nickname: str) -> bool:
        """post is received by the outbox
        Client to server message post
        https://www.w3.org/TR/activitypub/#client-to-server-outbox-delivery
        """
        city = self.server.city

        if post_to_nickname:
            print('Posting to nickname ' + post_to_nickname)
            self.post_to_nickname = post_to_nickname
            city = get_spoofed_city(self.server.city,
                                    self.server.base_dir,
                                    post_to_nickname, self.server.domain)

        shared_items_federated_domains = \
            self.server.shared_items_federated_domains
        shared_item_federation_tokens = \
            self.server.shared_item_federation_tokens
        return post_message_to_outbox(self.server.session,
                                      self.server.translate,
                                      message_json, self.post_to_nickname,
                                      self.server, self.server.base_dir,
                                      self.server.http_prefix,
                                      self.server.domain,
                                      self.server.domain_full,
                                      self.server.onion_domain,
                                      self.server.i2p_domain,
                                      self.server.port,
                                      self.server.recent_posts_cache,
                                      self.server.followers_threads,
                                      self.server.federation_list,
                                      self.server.send_threads,
                                      self.server.postLog,
                                      self.server.cached_webfingers,
                                      self.server.person_cache,
                                      self.server.allow_deletion,
                                      self.server.proxy_type, version,
                                      self.server.debug,
                                      self.server.yt_replace_domain,
                                      self.server.twitter_replacement_domain,
                                      self.server.show_published_date_only,
                                      self.server.allow_local_network_access,
                                      city, self.server.system_language,
                                      shared_items_federated_domains,
                                      shared_item_federation_tokens,
                                      self.server.low_bandwidth,
                                      self.server.signing_priv_key_pem,
                                      self.server.peertube_instances,
                                      self.server.theme_name,
                                      self.server.max_like_count,
                                      self.server.max_recent_posts,
                                      self.server.cw_lists,
                                      self.server.lists_enabled,
                                      self.server.content_license_url)

    def _get_outbox_thread_index(self, nickname: str,
                                 max_outbox_threads_per_account: int) -> int:
        """Returns the outbox thread index for the given account
        This is a ring buffer used to store the thread objects which
        are sending out posts
        """
        account_outbox_thread_name = nickname
        if not account_outbox_thread_name:
            account_outbox_thread_name = '*'

        # create the buffer for the given account
        if not self.server.outboxThread.get(account_outbox_thread_name):
            self.server.outboxThread[account_outbox_thread_name] = \
                [None] * max_outbox_threads_per_account
            self.server.outbox_thread_index[account_outbox_thread_name] = 0
            return 0

        # increment the ring buffer index
        index = self.server.outbox_thread_index[account_outbox_thread_name] + 1
        if index >= max_outbox_threads_per_account:
            index = 0

        self.server.outbox_thread_index[account_outbox_thread_name] = index

        # remove any existing thread from the current index in the buffer
        if self.server.outboxThread.get(account_outbox_thread_name):
            acct = account_outbox_thread_name
            if self.server.outboxThread[acct][index].is_alive():
                self.server.outboxThread[acct][index].kill()
        return index

    def _post_to_outbox_thread(self, message_json: {}) -> bool:
        """Creates a thread to send a post
        """
        account_outbox_thread_name = self.post_to_nickname
        if not account_outbox_thread_name:
            account_outbox_thread_name = '*'

        index = self._get_outbox_thread_index(account_outbox_thread_name, 8)

        print('Creating outbox thread ' +
              account_outbox_thread_name + '/' +
              str(self.server.outbox_thread_index[account_outbox_thread_name]))
        self.server.outboxThread[account_outbox_thread_name][index] = \
            thread_with_trace(target=self._post_to_outbox,
                              args=(message_json.copy(),
                                    self.server.project_version, None),
                              daemon=True)
        print('Starting outbox thread')
        self.server.outboxThread[account_outbox_thread_name][index].start()
        return True

    def _update_inbox_queue(self, nickname: str, message_json: {},
                            message_bytes: str) -> int:
        """Update the inbox queue
        """
        if self.server.restart_inbox_queue_in_progress:
            self._503()
            print('Message arrived but currently restarting inbox queue')
            self.server.postreq_busy = False
            return 2

        # check that the incoming message has a fully recognized
        # linked data context
        if not has_valid_context(message_json):
            print('Message arriving at inbox queue has no valid context')
            self._400()
            self.server.postreq_busy = False
            return 3

        # check for blocked domains so that they can be rejected early
        message_domain = None
        if not has_actor(message_json, self.server.debug):
            print('Message arriving at inbox queue has no actor')
            self._400()
            self.server.postreq_busy = False
            return 3

        # actor should be a string
        if not isinstance(message_json['actor'], str):
            self._400()
            self.server.postreq_busy = False
            return 3

        # check that some additional fields are strings
        string_fields = ('id', 'type', 'published')
        for check_field in string_fields:
            if not message_json.get(check_field):
                continue
            if not isinstance(message_json[check_field], str):
                self._400()
                self.server.postreq_busy = False
                return 3

        # check that to/cc fields are lists
        list_fields = ('to', 'cc')
        for check_field in list_fields:
            if not message_json.get(check_field):
                continue
            if not isinstance(message_json[check_field], list):
                self._400()
                self.server.postreq_busy = False
                return 3

        if has_object_dict(message_json):
            string_fields = (
                'id', 'actor', 'type', 'content', 'published',
                'summary', 'url', 'attributedTo'
            )
            for check_field in string_fields:
                if not message_json['object'].get(check_field):
                    continue
                if not isinstance(message_json['object'][check_field], str):
                    self._400()
                    self.server.postreq_busy = False
                    return 3
            # check that some fields are lists
            list_fields = ('to', 'cc', 'attachment')
            for check_field in list_fields:
                if not message_json['object'].get(check_field):
                    continue
                if not isinstance(message_json['object'][check_field], list):
                    self._400()
                    self.server.postreq_busy = False
                    return 3

        # actor should look like a url
        if '://' not in message_json['actor'] or \
           '.' not in message_json['actor']:
            print('POST actor does not look like a url ' +
                  message_json['actor'])
            self._400()
            self.server.postreq_busy = False
            return 3

        # sent by an actor on a local network address?
        if not self.server.allow_local_network_access:
            local_network_pattern_list = get_local_network_addresses()
            for local_network_pattern in local_network_pattern_list:
                if local_network_pattern in message_json['actor']:
                    print('POST actor contains local network address ' +
                          message_json['actor'])
                    self._400()
                    self.server.postreq_busy = False
                    return 3

        message_domain, _ = \
            get_domain_from_actor(message_json['actor'])

        self.server.blocked_cache_last_updated = \
            update_blocked_cache(self.server.base_dir,
                                 self.server.blocked_cache,
                                 self.server.blocked_cache_last_updated,
                                 self.server.blocked_cache_update_secs)

        if is_blocked_domain(self.server.base_dir, message_domain,
                             self.server.blocked_cache):
            print('POST from blocked domain ' + message_domain)
            self._400()
            self.server.postreq_busy = False
            return 3

        # if the inbox queue is full then return a busy code
        if len(self.server.inbox_queue) >= self.server.max_queue_length:
            if message_domain:
                print('Queue: Inbox queue is full. Incoming post from ' +
                      message_json['actor'])
            else:
                print('Queue: Inbox queue is full')
            self._503()
            clear_queue_items(self.server.base_dir, self.server.inbox_queue)
            if not self.server.restart_inbox_queue_in_progress:
                self.server.restart_inbox_queue = True
            self.server.postreq_busy = False
            return 2

        # Convert the headers needed for signature verification to dict
        headers_dict = {}
        headers_dict['host'] = self.headers['host']
        headers_dict['signature'] = self.headers['signature']
        if self.headers.get('Date'):
            headers_dict['Date'] = self.headers['Date']
        elif self.headers.get('date'):
            headers_dict['Date'] = self.headers['date']
        if self.headers.get('digest'):
            headers_dict['digest'] = self.headers['digest']
        if self.headers.get('Collection-Synchronization'):
            headers_dict['Collection-Synchronization'] = \
                self.headers['Collection-Synchronization']
        if self.headers.get('Content-type'):
            headers_dict['Content-type'] = self.headers['Content-type']
        if self.headers.get('Content-Length'):
            headers_dict['Content-Length'] = self.headers['Content-Length']
        elif self.headers.get('content-length'):
            headers_dict['content-length'] = self.headers['content-length']

        original_message_json = message_json.copy()

        # whether to add a 'to' field to the message
        add_to_field_types = (
            'Follow', 'Like', 'EmojiReact', 'Add', 'Remove', 'Ignore'
        )
        for add_to_type in add_to_field_types:
            message_json, _ = \
                add_to_field(add_to_type, message_json, self.server.debug)

        begin_save_time = time.time()
        # save the json for later queue processing
        message_bytes_decoded = message_bytes.decode('utf-8')

        if contains_invalid_local_links(message_bytes_decoded):
            print('WARN: post contains invalid local links ' +
                  str(original_message_json))
            return 5

        self.server.blocked_cache_last_updated = \
            update_blocked_cache(self.server.base_dir,
                                 self.server.blocked_cache,
                                 self.server.blocked_cache_last_updated,
                                 self.server.blocked_cache_update_secs)

        queue_filename = \
            save_post_to_inbox_queue(self.server.base_dir,
                                     self.server.http_prefix,
                                     nickname,
                                     self.server.domain_full,
                                     message_json, original_message_json,
                                     message_bytes_decoded,
                                     headers_dict,
                                     self.path,
                                     self.server.debug,
                                     self.server.blocked_cache,
                                     self.server.system_language)
        if queue_filename:
            # add json to the queue
            if queue_filename not in self.server.inbox_queue:
                self.server.inbox_queue.append(queue_filename)
            if self.server.debug:
                time_diff = int((time.time() - begin_save_time) * 1000)
                if time_diff > 200:
                    print('SLOW: slow save of inbox queue item ' +
                          queue_filename + ' took ' + str(time_diff) + ' mS')
            self.send_response(201)
            self.end_headers()
            self.server.postreq_busy = False
            return 0
        self._503()
        self.server.postreq_busy = False
        return 1

    def _is_authorized(self) -> bool:
        self.authorized_nickname = None

        not_auth_paths = (
            '/icons/', '/avatars/', '/favicons/',
            '/system/accounts/avatars/',
            '/system/accounts/headers/',
            '/system/media_attachments/files/',
            '/accounts/avatars/', '/accounts/headers/',
            '/favicon.ico', '/newswire.xml',
            '/newswire_favicon.ico', '/categories.xml'
        )
        for not_auth_str in not_auth_paths:
            if self.path.startswith(not_auth_str):
                return False

        # token based authenticated used by the web interface
        if self.headers.get('Cookie'):
            if self.headers['Cookie'].startswith('epicyon='):
                token_str = self.headers['Cookie'].split('=', 1)[1].strip()
                if ';' in token_str:
                    token_str = token_str.split(';')[0].strip()
                if self.server.tokens_lookup.get(token_str):
                    nickname = self.server.tokens_lookup[token_str]
                    if not is_system_account(nickname):
                        self.authorized_nickname = nickname
                        # default to the inbox of the person
                        if self.path == '/':
                            self.path = '/users/' + nickname + '/inbox'
                        # check that the path contains the same nickname
                        # as the cookie otherwise it would be possible
                        # to be authorized to use an account you don't own
                        if '/' + nickname + '/' in self.path:
                            return True
                        elif '/' + nickname + '?' in self.path:
                            return True
                        elif self.path.endswith('/' + nickname):
                            return True
                        if self.server.debug:
                            print('AUTH: nickname ' + nickname +
                                  ' was not found in path ' + self.path)
                    return False
                print('AUTH: epicyon cookie ' +
                      'authorization failed, header=' +
                      self.headers['Cookie'].replace('epicyon=', '') +
                      ' token_str=' + token_str + ' tokens=' +
                      str(self.server.tokens_lookup))
                return False
            print('AUTH: Header cookie was not authorized')
            return False
        # basic auth for c2s
        if self.headers.get('Authorization'):
            if authorize(self.server.base_dir, self.path,
                         self.headers['Authorization'],
                         self.server.debug):
                return True
            print('AUTH: C2S Basic auth did not authorize ' +
                  self.headers['Authorization'])
        return False

    def _clear_login_details(self, nickname: str, calling_domain: str) -> None:
        """Clears login details for the given account
        """
        # remove any token
        if self.server.tokens.get(nickname):
            del self.server.tokens_lookup[self.server.tokens[nickname]]
            del self.server.tokens[nickname]
        self._redirect_headers(self.server.http_prefix + '://' +
                               self.server.domain_full + '/login',
                               'epicyon=; SameSite=Strict',
                               calling_domain)

    def _show_login_screen(self, path: str, calling_domain: str, cookie: str,
                           base_dir: str, http_prefix: str,
                           domain: str, domain_full: str, port: int,
                           onion_domain: str, i2p_domain: str,
                           debug: bool) -> None:
        """Shows the login screen
        """
        # ensure that there is a minimum delay between failed login
        # attempts, to mitigate brute force
        if int(time.time()) - self.server.last_login_failure < 5:
            self._503()
            self.server.postreq_busy = False
            return

        # get the contents of POST containing login credentials
        length = int(self.headers['Content-length'])
        if length > 512:
            print('Login failed - credentials too long')
            self.send_response(401)
            self.end_headers()
            self.server.postreq_busy = False
            return

        try:
            login_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST login read ' +
                      'connection reset by peer')
            else:
                print('EX: POST login read socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST login read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        login_nickname, login_password, register = \
            html_get_login_credentials(login_params,
                                       self.server.last_login_time,
                                       self.server.domain)
        if login_nickname:
            if is_system_account(login_nickname):
                print('Invalid username login: ' + login_nickname +
                      ' (system account)')
                self._clear_login_details(login_nickname, calling_domain)
                self.server.postreq_busy = False
                return
            self.server.last_login_time = int(time.time())
            if register:
                if not valid_password(login_password):
                    self.server.postreq_busy = False
                    if calling_domain.endswith('.onion') and onion_domain:
                        self._redirect_headers('http://' + onion_domain +
                                               '/login', cookie,
                                               calling_domain)
                    elif (calling_domain.endswith('.i2p') and i2p_domain):
                        self._redirect_headers('http://' + i2p_domain +
                                               '/login', cookie,
                                               calling_domain)
                    else:
                        self._redirect_headers(http_prefix + '://' +
                                               domain_full + '/login',
                                               cookie, calling_domain)
                    return

                if not register_account(base_dir, http_prefix, domain, port,
                                        login_nickname, login_password,
                                        self.server.manual_follower_approval):
                    self.server.postreq_busy = False
                    if calling_domain.endswith('.onion') and onion_domain:
                        self._redirect_headers('http://' + onion_domain +
                                               '/login', cookie,
                                               calling_domain)
                    elif (calling_domain.endswith('.i2p') and i2p_domain):
                        self._redirect_headers('http://' + i2p_domain +
                                               '/login', cookie,
                                               calling_domain)
                    else:
                        self._redirect_headers(http_prefix + '://' +
                                               domain_full + '/login',
                                               cookie, calling_domain)
                    return
            auth_header = \
                create_basic_auth_header(login_nickname, login_password)
            if self.headers.get('X-Forward-For'):
                ip_address = self.headers['X-Forward-For']
            elif self.headers.get('X-Forwarded-For'):
                ip_address = self.headers['X-Forwarded-For']
            else:
                ip_address = self.client_address[0]
            if not domain.endswith('.onion'):
                if not is_local_network_address(ip_address):
                    print('Login attempt from IP: ' + str(ip_address))
            if not authorize_basic(base_dir, '/users/' +
                                   login_nickname + '/outbox',
                                   auth_header, False):
                print('Login failed: ' + login_nickname)
                self._clear_login_details(login_nickname, calling_domain)
                fail_time = int(time.time())
                self.server.last_login_failure = fail_time
                if not domain.endswith('.onion'):
                    if not is_local_network_address(ip_address):
                        record_login_failure(base_dir, ip_address,
                                             self.server.login_failure_count,
                                             fail_time,
                                             self.server.log_login_failures)
                self.server.postreq_busy = False
                return
            else:
                if self.server.login_failure_count.get(ip_address):
                    del self.server.login_failure_count[ip_address]
                if is_suspended(base_dir, login_nickname):
                    msg = \
                        html_suspended(self.server.css_cache,
                                       base_dir).encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
                # login success - redirect with authorization
                print('Login success: ' + login_nickname)
                # re-activate account if needed
                activate_account(base_dir, login_nickname, domain)
                # This produces a deterministic token based
                # on nick+password+salt
                salt_filename = \
                    acct_dir(base_dir, login_nickname, domain) + '/.salt'
                salt = create_password(32)
                if os.path.isfile(salt_filename):
                    try:
                        with open(salt_filename, 'r') as fp_salt:
                            salt = fp_salt.read()
                    except OSError as ex:
                        print('EX: Unable to read salt for ' +
                              login_nickname + ' ' + str(ex))
                else:
                    try:
                        with open(salt_filename, 'w+') as fp_salt:
                            fp_salt.write(salt)
                    except OSError as ex:
                        print('EX: Unable to save salt for ' +
                              login_nickname + ' ' + str(ex))

                token_text = login_nickname + login_password + salt
                token = sha256(token_text.encode('utf-8')).hexdigest()
                self.server.tokens[login_nickname] = token
                login_handle = login_nickname + '@' + domain
                token_filename = \
                    base_dir + '/accounts/' + \
                    login_handle + '/.token'
                try:
                    with open(token_filename, 'w+') as fp_tok:
                        fp_tok.write(token)
                except OSError as ex:
                    print('EX: Unable to save token for ' +
                          login_nickname + ' ' + str(ex))

                person_upgrade_actor(base_dir, None, login_handle,
                                     base_dir + '/accounts/' +
                                     login_handle + '.json')

                index = self.server.tokens[login_nickname]
                self.server.tokens_lookup[index] = login_nickname
                cookie_str = 'SET:epicyon=' + \
                    self.server.tokens[login_nickname] + '; SameSite=Strict'
                if calling_domain.endswith('.onion') and onion_domain:
                    self._redirect_headers('http://' +
                                           onion_domain +
                                           '/users/' +
                                           login_nickname + '/' +
                                           self.server.default_timeline,
                                           cookie_str, calling_domain)
                elif (calling_domain.endswith('.i2p') and i2p_domain):
                    self._redirect_headers('http://' +
                                           i2p_domain +
                                           '/users/' +
                                           login_nickname + '/' +
                                           self.server.default_timeline,
                                           cookie_str, calling_domain)
                else:
                    self._redirect_headers(http_prefix + '://' +
                                           domain_full + '/users/' +
                                           login_nickname + '/' +
                                           self.server.default_timeline,
                                           cookie_str, calling_domain)
                self.server.postreq_busy = False
                return
        self._200()
        self.server.postreq_busy = False

    def _moderator_actions(self, path: str, calling_domain: str, cookie: str,
                           base_dir: str, http_prefix: str,
                           domain: str, domain_full: str, port: int,
                           onion_domain: str, i2p_domain: str,
                           debug: bool) -> None:
        """Actions on the moderator screen
        """
        users_path = path.replace('/moderationaction', '')
        nickname = users_path.replace('/users/', '')
        actor_str = self._get_instance_url(calling_domain) + users_path
        if not is_moderator(self.server.base_dir, nickname):
            self._redirect_headers(actor_str + '/moderation',
                                   cookie, calling_domain)
            self.server.postreq_busy = False
            return

        length = int(self.headers['Content-length'])

        try:
            moderation_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST moderation_params connection was reset')
            else:
                print('EX: POST moderation_params ' +
                      'rfile.read socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST moderation_params rfile.read failed, ' +
                  str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if '&' in moderation_params:
            moderation_text = None
            moderation_button = None
            for moderation_str in moderation_params.split('&'):
                if moderation_str.startswith('moderationAction'):
                    if '=' in moderation_str:
                        moderation_text = \
                            moderation_str.split('=')[1].strip()
                        mod_text = moderation_text.replace('+', ' ')
                        moderation_text = \
                            urllib.parse.unquote_plus(mod_text.strip())
                elif moderation_str.startswith('submitInfo'):
                    if '=' in moderation_str:
                        moderation_text = \
                            moderation_str.split('=')[1].strip()
                        mod_text = moderation_text.replace('+', ' ')
                        moderation_text = \
                            urllib.parse.unquote_plus(mod_text.strip())
                    search_handle = moderation_text
                    if search_handle:
                        if '/@' in search_handle:
                            search_nickname = \
                                get_nickname_from_actor(search_handle)
                            search_domain, _ = \
                                get_domain_from_actor(search_handle)
                            search_handle = \
                                search_nickname + '@' + search_domain
                        if '@' not in search_handle:
                            if search_handle.startswith('http'):
                                search_nickname = \
                                    get_nickname_from_actor(search_handle)
                                search_domain, _ = \
                                    get_domain_from_actor(search_handle)
                                search_handle = \
                                    search_nickname + '@' + search_domain
                        if '@' not in search_handle:
                            # is this a local nickname on this instance?
                            local_handle = \
                                search_handle + '@' + self.server.domain
                            if os.path.isdir(self.server.base_dir +
                                             '/accounts/' + local_handle):
                                search_handle = local_handle
                            else:
                                search_handle = None
                    if search_handle:
                        msg = \
                            html_account_info(self.server.css_cache,
                                              self.server.translate,
                                              base_dir, http_prefix,
                                              nickname,
                                              self.server.domain,
                                              self.server.port,
                                              search_handle,
                                              self.server.debug,
                                              self.server.system_language,
                                              self.server.signing_priv_key_pem)
                    else:
                        msg = \
                            html_moderation_info(self.server.css_cache,
                                                 self.server.translate,
                                                 base_dir, http_prefix,
                                                 nickname)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
                elif moderation_str.startswith('submitBlock'):
                    moderation_button = 'block'
                elif moderation_str.startswith('submitUnblock'):
                    moderation_button = 'unblock'
                elif moderation_str.startswith('submitFilter'):
                    moderation_button = 'filter'
                elif moderation_str.startswith('submitUnfilter'):
                    moderation_button = 'unfilter'
                elif moderation_str.startswith('submitSuspend'):
                    moderation_button = 'suspend'
                elif moderation_str.startswith('submitUnsuspend'):
                    moderation_button = 'unsuspend'
                elif moderation_str.startswith('submitRemove'):
                    moderation_button = 'remove'
            if moderation_button and moderation_text:
                if debug:
                    print('moderation_button: ' + moderation_button)
                    print('moderation_text: ' + moderation_text)
                nickname = moderation_text
                if nickname.startswith('http') or \
                   nickname.startswith('hyper'):
                    nickname = get_nickname_from_actor(nickname)
                if '@' in nickname:
                    nickname = nickname.split('@')[0]
                if moderation_button == 'suspend':
                    suspend_account(base_dir, nickname, domain)
                if moderation_button == 'unsuspend':
                    reenable_account(base_dir, nickname)
                if moderation_button == 'filter':
                    add_global_filter(base_dir, moderation_text)
                if moderation_button == 'unfilter':
                    remove_global_filter(base_dir, moderation_text)
                if moderation_button == 'block':
                    full_block_domain = None
                    if moderation_text.startswith('http') or \
                       moderation_text.startswith('hyper'):
                        # https://domain
                        block_domain, block_port = \
                            get_domain_from_actor(moderation_text)
                        full_block_domain = \
                            get_full_domain(block_domain, block_port)
                    if '@' in moderation_text:
                        # nick@domain or *@domain
                        full_block_domain = moderation_text.split('@')[1]
                    else:
                        # assume the text is a domain name
                        if not full_block_domain and '.' in moderation_text:
                            nickname = '*'
                            full_block_domain = moderation_text.strip()
                    if full_block_domain or nickname.startswith('#'):
                        add_global_block(base_dir, nickname, full_block_domain)
                if moderation_button == 'unblock':
                    full_block_domain = None
                    if moderation_text.startswith('http') or \
                       moderation_text.startswith('hyper'):
                        # https://domain
                        block_domain, block_port = \
                            get_domain_from_actor(moderation_text)
                        full_block_domain = \
                            get_full_domain(block_domain, block_port)
                    if '@' in moderation_text:
                        # nick@domain or *@domain
                        full_block_domain = moderation_text.split('@')[1]
                    else:
                        # assume the text is a domain name
                        if not full_block_domain and '.' in moderation_text:
                            nickname = '*'
                            full_block_domain = moderation_text.strip()
                    if full_block_domain or nickname.startswith('#'):
                        remove_global_block(base_dir, nickname,
                                            full_block_domain)
                if moderation_button == 'remove':
                    if '/statuses/' not in moderation_text:
                        remove_account(base_dir, nickname, domain, port)
                    else:
                        # remove a post or thread
                        post_filename = \
                            locate_post(base_dir, nickname, domain,
                                        moderation_text)
                        if post_filename:
                            if can_remove_post(base_dir,
                                               nickname, domain, port,
                                               moderation_text):
                                delete_post(base_dir,
                                            http_prefix,
                                            nickname, domain,
                                            post_filename,
                                            debug,
                                            self.server.recent_posts_cache)
                        if nickname != 'news':
                            # if this is a local blog post then also remove it
                            # from the news actor
                            post_filename = \
                                locate_post(base_dir, 'news', domain,
                                            moderation_text)
                            if post_filename:
                                if can_remove_post(base_dir,
                                                   'news', domain, port,
                                                   moderation_text):
                                    delete_post(base_dir,
                                                http_prefix,
                                                'news', domain,
                                                post_filename,
                                                debug,
                                                self.server.recent_posts_cache)

        self._redirect_headers(actor_str + '/moderation',
                               cookie, calling_domain)
        self.server.postreq_busy = False
        return

    def _key_shortcuts(self, path: str,
                       calling_domain: str, cookie: str,
                       base_dir: str, http_prefix: str, nickname: str,
                       domain: str, domain_full: str, port: int,
                       onion_domain: str, i2p_domain: str,
                       debug: bool, access_keys: {},
                       default_timeline: str) -> None:
        """Receive POST from webapp_accesskeys
        """
        users_path = '/users/' + nickname
        origin_path_str = \
            http_prefix + '://' + domain_full + users_path + '/' + \
            default_timeline
        length = int(self.headers['Content-length'])

        try:
            access_keys_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST access_keys_params ' +
                      'connection reset by peer')
            else:
                print('EX: POST access_keys_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST access_keys_params rfile.read failed, ' +
                  str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        access_keys_params = \
            urllib.parse.unquote_plus(access_keys_params)

        # key shortcuts screen, back button
        # See html_access_keys
        if 'submitAccessKeysCancel=' in access_keys_params or \
           'submitAccessKeys=' not in access_keys_params:
            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str = \
                    'http://' + onion_domain + users_path + '/' + \
                    default_timeline
            elif calling_domain.endswith('.i2p') and i2p_domain:
                origin_path_str = \
                    'http://' + i2p_domain + users_path + \
                    '/' + default_timeline
            self._redirect_headers(origin_path_str, cookie, calling_domain)
            self.server.postreq_busy = False
            return

        save_keys = False
        access_keys_template = self.server.access_keys
        for variable_name, _ in access_keys_template.items():
            if not access_keys.get(variable_name):
                access_keys[variable_name] = \
                    access_keys_template[variable_name]

            variable_name2 = variable_name.replace(' ', '_')
            if variable_name2 + '=' in access_keys_params:
                new_key = access_keys_params.split(variable_name2 + '=')[1]
                if '&' in new_key:
                    new_key = new_key.split('&')[0]
                if new_key:
                    if len(new_key) > 1:
                        new_key = new_key[0]
                    if new_key != access_keys[variable_name]:
                        access_keys[variable_name] = new_key
                        save_keys = True

        if save_keys:
            access_keys_filename = \
                acct_dir(base_dir, nickname, domain) + '/access_keys.json'
            save_json(access_keys, access_keys_filename)
            if not self.server.key_shortcuts.get(nickname):
                self.server.key_shortcuts[nickname] = access_keys.copy()

        # redirect back from key shortcuts screen
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = \
                'http://' + onion_domain + users_path + '/' + default_timeline
        elif calling_domain.endswith('.i2p') and i2p_domain:
            origin_path_str = \
                'http://' + i2p_domain + users_path + '/' + default_timeline
        self._redirect_headers(origin_path_str, cookie, calling_domain)
        self.server.postreq_busy = False
        return

    def _theme_designer_edit(self, path: str,
                             calling_domain: str, cookie: str,
                             base_dir: str, http_prefix: str, nickname: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             debug: bool, access_keys: {},
                             default_timeline: str, theme_name: str,
                             allow_local_network_access: bool,
                             system_language: str,
                             dyslexic_font: bool) -> None:
        """Receive POST from webapp_theme_designer
        """
        users_path = '/users/' + nickname
        origin_path_str = \
            http_prefix + '://' + domain_full + users_path + '/' + \
            default_timeline
        length = int(self.headers['Content-length'])

        try:
            theme_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST theme_params ' +
                      'connection reset by peer')
            else:
                print('EX: POST theme_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST theme_params rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        theme_params = \
            urllib.parse.unquote_plus(theme_params)

        # theme designer screen, reset button
        # See html_theme_designer
        if 'submitThemeDesignerReset=' in theme_params or \
           'submitThemeDesigner=' not in theme_params:
            if 'submitThemeDesignerReset=' in theme_params:
                reset_theme_designer_settings(base_dir, theme_name, domain,
                                              allow_local_network_access,
                                              system_language)
                set_theme(base_dir, theme_name, domain,
                          allow_local_network_access, system_language,
                          dyslexic_font)

            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str = \
                    'http://' + onion_domain + users_path + '/' + \
                    default_timeline
            elif calling_domain.endswith('.i2p') and i2p_domain:
                origin_path_str = \
                    'http://' + i2p_domain + users_path + \
                    '/' + default_timeline
            self._redirect_headers(origin_path_str, cookie, calling_domain)
            self.server.postreq_busy = False
            return

        fields = {}
        fields_list = theme_params.split('&')
        for field_str in fields_list:
            if '=' not in field_str:
                continue
            field_value = field_str.split('=')[1].strip()
            if not field_value:
                continue
            if field_value == 'on':
                field_value = 'True'
            fields_index = field_str.split('=')[0]
            fields[fields_index] = field_value

        # Check for boolean values which are False.
        # These don't come through via theme_params,
        # so need to be checked separately
        theme_filename = base_dir + '/theme/' + theme_name + '/theme.json'
        theme_json = load_json(theme_filename)
        if theme_json:
            for variable_name, value in theme_json.items():
                variable_name = 'themeSetting_' + variable_name
                if value.lower() == 'false' or value.lower() == 'true':
                    if variable_name not in fields:
                        fields[variable_name] = 'False'

        # get the parameters from the theme designer screen
        theme_designer_params = {}
        for variable_name, key in fields.items():
            if variable_name.startswith('themeSetting_'):
                variable_name = variable_name.replace('themeSetting_', '')
                theme_designer_params[variable_name] = key

        set_theme_from_designer(base_dir, theme_name, domain,
                                theme_designer_params,
                                allow_local_network_access,
                                system_language, dyslexic_font)

        # set boolean values
        if 'rss-icon-at-top' in theme_designer_params:
            if theme_designer_params['rss-icon-at-top'].lower() == 'true':
                self.server.rss_icon_at_top = True
            else:
                self.server.rss_icon_at_top = False
        if 'publish-button-at-top' in theme_designer_params:
            publish_button_at_top_str = \
                theme_designer_params['publish-button-at-top'].lower()
            if publish_button_at_top_str == 'true':
                self.server.publish_button_at_top = True
            else:
                self.server.publish_button_at_top = False
        if 'newswire-publish-icon' in theme_designer_params:
            newswire_publish_icon_str = \
                theme_designer_params['newswire-publish-icon'].lower()
            if newswire_publish_icon_str == 'true':
                self.server.show_publish_as_icon = True
            else:
                self.server.show_publish_as_icon = False
        if 'icons-as-buttons' in theme_designer_params:
            if theme_designer_params['icons-as-buttons'].lower() == 'true':
                self.server.icons_as_buttons = True
            else:
                self.server.icons_as_buttons = False
        if 'full-width-timeline-buttons' in theme_designer_params:
            theme_value = theme_designer_params['full-width-timeline-buttons']
            if theme_value.lower() == 'true':
                self.server.full_width_tl_button_header = True
            else:
                self.server.full_width_tl_button_header = False

        # redirect back from theme designer screen
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = \
                'http://' + onion_domain + users_path + '/' + default_timeline
        elif calling_domain.endswith('.i2p') and i2p_domain:
            origin_path_str = \
                'http://' + i2p_domain + users_path + '/' + default_timeline
        self._redirect_headers(origin_path_str, cookie, calling_domain)
        self.server.postreq_busy = False
        return

    def _person_options(self, path: str,
                        calling_domain: str, cookie: str,
                        base_dir: str, http_prefix: str,
                        domain: str, domain_full: str, port: int,
                        onion_domain: str, i2p_domain: str,
                        debug: bool) -> None:
        """Receive POST from person options screen
        """
        page_number = 1
        users_path = path.split('/personoptions')[0]
        origin_path_str = http_prefix + '://' + domain_full + users_path

        chooser_nickname = get_nickname_from_actor(origin_path_str)
        if not chooser_nickname:
            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str = 'http://' + onion_domain + users_path
            elif (calling_domain.endswith('.i2p') and i2p_domain):
                origin_path_str = 'http://' + i2p_domain + users_path
            print('WARN: unable to find nickname in ' + origin_path_str)
            self._redirect_headers(origin_path_str, cookie, calling_domain)
            self.server.postreq_busy = False
            return

        length = int(self.headers['Content-length'])

        try:
            options_confirm_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST options_confirm_params ' +
                      'connection reset by peer')
            else:
                print('EX: POST options_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: ' +
                  'POST options_confirm_params rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        options_confirm_params = \
            urllib.parse.unquote_plus(options_confirm_params)

        # page number to return to
        if 'pageNumber=' in options_confirm_params:
            page_number_str = options_confirm_params.split('pageNumber=')[1]
            if '&' in page_number_str:
                page_number_str = page_number_str.split('&')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)

        # actor for the person
        options_actor = options_confirm_params.split('actor=')[1]
        if '&' in options_actor:
            options_actor = options_actor.split('&')[0]

        # url of the avatar
        options_avatar_url = options_confirm_params.split('avatarUrl=')[1]
        if '&' in options_avatar_url:
            options_avatar_url = options_avatar_url.split('&')[0]

        # link to a post, which can then be included in reports
        post_url = None
        if 'postUrl' in options_confirm_params:
            post_url = options_confirm_params.split('postUrl=')[1]
            if '&' in post_url:
                post_url = post_url.split('&')[0]

        # petname for this person
        petname = None
        if 'optionpetname' in options_confirm_params:
            petname = options_confirm_params.split('optionpetname=')[1]
            if '&' in petname:
                petname = petname.split('&')[0]
            # Limit the length of the petname
            if len(petname) > 20 or \
               ' ' in petname or '/' in petname or \
               '?' in petname or '#' in petname:
                petname = None

        # notes about this person
        person_notes = None
        if 'optionnotes' in options_confirm_params:
            person_notes = options_confirm_params.split('optionnotes=')[1]
            if '&' in person_notes:
                person_notes = person_notes.split('&')[0]
            person_notes = urllib.parse.unquote_plus(person_notes.strip())
            # Limit the length of the notes
            if len(person_notes) > 64000:
                person_notes = None

        # get the nickname
        options_nickname = get_nickname_from_actor(options_actor)
        if not options_nickname:
            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str = 'http://' + onion_domain + users_path
            elif (calling_domain.endswith('.i2p') and i2p_domain):
                origin_path_str = 'http://' + i2p_domain + users_path
            print('WARN: unable to find nickname in ' + options_actor)
            self._redirect_headers(origin_path_str, cookie, calling_domain)
            self.server.postreq_busy = False
            return

        options_domain, options_port = get_domain_from_actor(options_actor)
        options_domain_full = get_full_domain(options_domain, options_port)
        if chooser_nickname == options_nickname and \
           options_domain == domain and \
           options_port == port:
            if debug:
                print('You cannot perform an option action on yourself')

        # person options screen, view button
        # See html_person_options
        if '&submitView=' in options_confirm_params:
            if debug:
                print('Viewing ' + options_actor)
            self._redirect_headers(options_actor,
                                   cookie, calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, petname submit button
        # See html_person_options
        if '&submitPetname=' in options_confirm_params and petname:
            if debug:
                print('Change petname to ' + petname)
            handle = options_nickname + '@' + options_domain_full
            set_pet_name(base_dir,
                         chooser_nickname,
                         domain,
                         handle, petname)
            users_path_str = \
                users_path + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(users_path_str, cookie,
                                   calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, person notes submit button
        # See html_person_options
        if '&submitPersonNotes=' in options_confirm_params:
            if debug:
                print('Change person notes')
            handle = options_nickname + '@' + options_domain_full
            if not person_notes:
                person_notes = ''
            set_person_notes(base_dir,
                             chooser_nickname,
                             domain,
                             handle, person_notes)
            users_path_str = \
                users_path + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(users_path_str, cookie,
                                   calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, on calendar checkbox
        # See html_person_options
        if '&submitOnCalendar=' in options_confirm_params:
            on_calendar = None
            if 'onCalendar=' in options_confirm_params:
                on_calendar = options_confirm_params.split('onCalendar=')[1]
                if '&' in on_calendar:
                    on_calendar = on_calendar.split('&')[0]
            if on_calendar == 'on':
                add_person_to_calendar(base_dir,
                                       chooser_nickname,
                                       domain,
                                       options_nickname,
                                       options_domain_full)
            else:
                remove_person_from_calendar(base_dir,
                                            chooser_nickname,
                                            domain,
                                            options_nickname,
                                            options_domain_full)
            users_path_str = \
                users_path + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(users_path_str, cookie,
                                   calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, on notify checkbox
        # See html_person_options
        if '&submitNotifyOnPost=' in options_confirm_params:
            notify = None
            if 'notifyOnPost=' in options_confirm_params:
                notify = options_confirm_params.split('notifyOnPost=')[1]
                if '&' in notify:
                    notify = notify.split('&')[0]
            if notify == 'on':
                add_notify_on_post(base_dir,
                                   chooser_nickname,
                                   domain,
                                   options_nickname,
                                   options_domain_full)
            else:
                remove_notify_on_post(base_dir,
                                      chooser_nickname,
                                      domain,
                                      options_nickname,
                                      options_domain_full)
            users_path_str = \
                users_path + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(users_path_str, cookie,
                                   calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, permission to post to newswire
        # See html_person_options
        if '&submitPostToNews=' in options_confirm_params:
            admin_nickname = get_config_param(self.server.base_dir, 'admin')
            if (chooser_nickname != options_nickname and
                (chooser_nickname == admin_nickname or
                 (is_moderator(self.server.base_dir, chooser_nickname) and
                  not is_moderator(self.server.base_dir, options_nickname)))):
                posts_to_news = None
                if 'postsToNews=' in options_confirm_params:
                    posts_to_news = \
                        options_confirm_params.split('postsToNews=')[1]
                    if '&' in posts_to_news:
                        posts_to_news = posts_to_news.split('&')[0]
                account_dir = acct_dir(self.server.base_dir,
                                       options_nickname, options_domain)
                newswire_blocked_filename = account_dir + '/.nonewswire'
                if posts_to_news == 'on':
                    if os.path.isfile(newswire_blocked_filename):
                        try:
                            os.remove(newswire_blocked_filename)
                        except OSError:
                            print('EX: _person_options unable to delete ' +
                                  newswire_blocked_filename)
                        refresh_newswire(self.server.base_dir)
                else:
                    if os.path.isdir(account_dir):
                        nw_filename = newswire_blocked_filename
                        nw_written = False
                        try:
                            with open(nw_filename, 'w+') as nofile:
                                nofile.write('\n')
                                nw_written = True
                        except OSError as ex:
                            print('EX: unable to write ' + nw_filename +
                                  ' ' + str(ex))
                        if nw_written:
                            refresh_newswire(self.server.base_dir)
            users_path_str = \
                users_path + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(users_path_str, cookie,
                                   calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, permission to post to featured articles
        # See html_person_options
        if '&submitPostToFeatures=' in options_confirm_params:
            admin_nickname = get_config_param(self.server.base_dir, 'admin')
            if (chooser_nickname != options_nickname and
                (chooser_nickname == admin_nickname or
                 (is_moderator(self.server.base_dir, chooser_nickname) and
                  not is_moderator(self.server.base_dir, options_nickname)))):
                posts_to_features = None
                if 'postsToFeatures=' in options_confirm_params:
                    posts_to_features = \
                        options_confirm_params.split('postsToFeatures=')[1]
                    if '&' in posts_to_features:
                        posts_to_features = posts_to_features.split('&')[0]
                account_dir = acct_dir(self.server.base_dir,
                                       options_nickname, options_domain)
                features_blocked_filename = account_dir + '/.nofeatures'
                if posts_to_features == 'on':
                    if os.path.isfile(features_blocked_filename):
                        try:
                            os.remove(features_blocked_filename)
                        except OSError:
                            print('EX: _person_options unable to delete ' +
                                  features_blocked_filename)
                        refresh_newswire(self.server.base_dir)
                else:
                    if os.path.isdir(account_dir):
                        feat_filename = features_blocked_filename
                        feat_written = False
                        try:
                            with open(feat_filename, 'w+') as nofile:
                                nofile.write('\n')
                                feat_written = True
                        except OSError as ex:
                            print('EX: unable to write ' + feat_filename +
                                  ' ' + str(ex))
                        if feat_written:
                            refresh_newswire(self.server.base_dir)
            users_path_str = \
                users_path + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(users_path_str, cookie,
                                   calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, permission to post to newswire
        # See html_person_options
        if '&submitModNewsPosts=' in options_confirm_params:
            admin_nickname = get_config_param(self.server.base_dir, 'admin')
            if (chooser_nickname != options_nickname and
                (chooser_nickname == admin_nickname or
                 (is_moderator(self.server.base_dir, chooser_nickname) and
                  not is_moderator(self.server.base_dir, options_nickname)))):
                mod_posts_to_news = None
                if 'modNewsPosts=' in options_confirm_params:
                    mod_posts_to_news = \
                        options_confirm_params.split('modNewsPosts=')[1]
                    if '&' in mod_posts_to_news:
                        mod_posts_to_news = mod_posts_to_news.split('&')[0]
                account_dir = acct_dir(self.server.base_dir,
                                       options_nickname, options_domain)
                newswire_mod_filename = account_dir + '/.newswiremoderated'
                if mod_posts_to_news != 'on':
                    if os.path.isfile(newswire_mod_filename):
                        try:
                            os.remove(newswire_mod_filename)
                        except OSError:
                            print('EX: _person_options unable to delete ' +
                                  newswire_mod_filename)
                else:
                    if os.path.isdir(account_dir):
                        nw_filename = newswire_mod_filename
                        try:
                            with open(nw_filename, 'w+') as modfile:
                                modfile.write('\n')
                        except OSError:
                            print('EX: unable to write ' + nw_filename)
            users_path_str = \
                users_path + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(users_path_str, cookie,
                                   calling_domain)
            self.server.postreq_busy = False
            return

        # person options screen, block button
        # See html_person_options
        if '&submitBlock=' in options_confirm_params:
            print('Adding block by ' + chooser_nickname +
                  ' of ' + options_actor)
            if add_block(base_dir, chooser_nickname,
                         domain,
                         options_nickname, options_domain_full):
                # send block activity
                self._send_block(http_prefix,
                                 chooser_nickname, domain_full,
                                 options_nickname, options_domain_full)

        # person options screen, unblock button
        # See html_person_options
        if '&submitUnblock=' in options_confirm_params:
            if debug:
                print('Unblocking ' + options_actor)
            msg = \
                html_confirm_unblock(self.server.css_cache,
                                     self.server.translate,
                                     base_dir,
                                     users_path,
                                     options_actor,
                                     options_avatar_url).encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            self.server.postreq_busy = False
            return

        # person options screen, follow button
        # See html_person_options followStr
        if '&submitFollow=' in options_confirm_params or \
           '&submitJoin=' in options_confirm_params:
            if debug:
                print('Following ' + options_actor)
            msg = \
                html_confirm_follow(self.server.css_cache,
                                    self.server.translate,
                                    base_dir,
                                    users_path,
                                    options_actor,
                                    options_avatar_url).encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            self.server.postreq_busy = False
            return

        # person options screen, unfollow button
        # See html_person_options followStr
        if '&submitUnfollow=' in options_confirm_params or \
           '&submitLeave=' in options_confirm_params:
            print('Unfollowing ' + options_actor)
            msg = \
                html_confirm_unfollow(self.server.css_cache,
                                      self.server.translate,
                                      base_dir,
                                      users_path,
                                      options_actor,
                                      options_avatar_url).encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            self.server.postreq_busy = False
            return

        # person options screen, DM button
        # See html_person_options
        if '&submitDM=' in options_confirm_params:
            if debug:
                print('Sending DM to ' + options_actor)
            report_path = path.replace('/personoptions', '') + '/newdm'

            access_keys = self.server.access_keys
            if '/users/' in path:
                nickname = path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]

            custom_submit_text = get_config_param(base_dir, 'customSubmitText')
            conversation_id = None
            msg = html_new_post(self.server.css_cache,
                                False, self.server.translate,
                                base_dir,
                                http_prefix,
                                report_path, None,
                                [options_actor], None, None,
                                page_number, '',
                                chooser_nickname,
                                domain,
                                domain_full,
                                self.server.default_timeline,
                                self.server.newswire,
                                self.server.theme_name,
                                True, access_keys,
                                custom_submit_text,
                                conversation_id,
                                self.server.recent_posts_cache,
                                self.server.max_recent_posts,
                                self.server.session,
                                self.server.cached_webfingers,
                                self.server.person_cache,
                                self.server.port,
                                None,
                                self.server.project_version,
                                self.server.yt_replace_domain,
                                self.server.twitter_replacement_domain,
                                self.server.show_published_date_only,
                                self.server.peertube_instances,
                                self.server.allow_local_network_access,
                                self.server.system_language,
                                self.server.max_like_count,
                                self.server.signing_priv_key_pem,
                                self.server.cw_lists,
                                self.server.lists_enabled,
                                self.server.default_timeline).encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            self.server.postreq_busy = False
            return

        # person options screen, Info button
        # See html_person_options
        if '&submitPersonInfo=' in options_confirm_params:
            if is_moderator(self.server.base_dir, chooser_nickname):
                if debug:
                    print('Showing info for ' + options_actor)
                signing_priv_key_pem = self.server.signing_priv_key_pem
                msg = \
                    html_account_info(self.server.css_cache,
                                      self.server.translate,
                                      base_dir,
                                      http_prefix,
                                      chooser_nickname,
                                      domain,
                                      self.server.port,
                                      options_actor,
                                      self.server.debug,
                                      self.server.system_language,
                                      signing_priv_key_pem).encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
                self.server.postreq_busy = False
                return
            else:
                self._404()
                return

        # person options screen, snooze button
        # See html_person_options
        if '&submitSnooze=' in options_confirm_params:
            users_path = path.split('/personoptions')[0]
            this_actor = http_prefix + '://' + domain_full + users_path
            if debug:
                print('Snoozing ' + options_actor + ' ' + this_actor)
            if '/users/' in this_actor:
                nickname = this_actor.split('/users/')[1]
                person_snooze(base_dir, nickname,
                              domain, options_actor)
                if calling_domain.endswith('.onion') and onion_domain:
                    this_actor = 'http://' + onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and i2p_domain):
                    this_actor = 'http://' + i2p_domain + users_path
                actor_path_str = \
                    this_actor + '/' + self.server.default_timeline + \
                    '?page=' + str(page_number)
                self._redirect_headers(actor_path_str, cookie,
                                       calling_domain)
                self.server.postreq_busy = False
                return

        # person options screen, unsnooze button
        # See html_person_options
        if '&submitUnSnooze=' in options_confirm_params:
            users_path = path.split('/personoptions')[0]
            this_actor = http_prefix + '://' + domain_full + users_path
            if debug:
                print('Unsnoozing ' + options_actor + ' ' + this_actor)
            if '/users/' in this_actor:
                nickname = this_actor.split('/users/')[1]
                person_unsnooze(base_dir, nickname,
                                domain, options_actor)
                if calling_domain.endswith('.onion') and onion_domain:
                    this_actor = 'http://' + onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and i2p_domain):
                    this_actor = 'http://' + i2p_domain + users_path
                actor_path_str = \
                    this_actor + '/' + self.server.default_timeline + \
                    '?page=' + str(page_number)
                self._redirect_headers(actor_path_str, cookie,
                                       calling_domain)
                self.server.postreq_busy = False
                return

        # person options screen, report button
        # See html_person_options
        if '&submitReport=' in options_confirm_params:
            if debug:
                print('Reporting ' + options_actor)
            report_path = \
                path.replace('/personoptions', '') + '/newreport'

            access_keys = self.server.access_keys
            if '/users/' in path:
                nickname = path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]

            custom_submit_text = get_config_param(base_dir, 'customSubmitText')
            conversation_id = None
            msg = html_new_post(self.server.css_cache,
                                False, self.server.translate,
                                base_dir,
                                http_prefix,
                                report_path, None, [],
                                None, post_url, page_number, '',
                                chooser_nickname,
                                domain,
                                domain_full,
                                self.server.default_timeline,
                                self.server.newswire,
                                self.server.theme_name,
                                True, access_keys,
                                custom_submit_text,
                                conversation_id,
                                self.server.recent_posts_cache,
                                self.server.max_recent_posts,
                                self.server.session,
                                self.server.cached_webfingers,
                                self.server.person_cache,
                                self.server.port,
                                None,
                                self.server.project_version,
                                self.server.yt_replace_domain,
                                self.server.twitter_replacement_domain,
                                self.server.show_published_date_only,
                                self.server.peertube_instances,
                                self.server.allow_local_network_access,
                                self.server.system_language,
                                self.server.max_like_count,
                                self.server.signing_priv_key_pem,
                                self.server.cw_lists,
                                self.server.lists_enabled,
                                self.server.default_timeline).encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            self.server.postreq_busy = False
            return

        # redirect back from person options screen
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif calling_domain.endswith('.i2p') and i2p_domain:
            origin_path_str = 'http://' + i2p_domain + users_path
        self._redirect_headers(origin_path_str, cookie, calling_domain)
        self.server.postreq_busy = False
        return

    def _unfollow_confirm(self, calling_domain: str, cookie: str,
                          authorized: bool, path: str,
                          base_dir: str, http_prefix: str,
                          domain: str, domain_full: str, port: int,
                          onion_domain: str, i2p_domain: str,
                          debug: bool) -> None:
        """Confirm to unfollow
        """
        users_path = path.split('/unfollowconfirm')[0]
        origin_path_str = http_prefix + '://' + domain_full + users_path
        follower_nickname = get_nickname_from_actor(origin_path_str)

        length = int(self.headers['Content-length'])

        try:
            follow_confirm_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST follow_confirm_params ' +
                      'connection was reset')
            else:
                print('EX: POST follow_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST follow_confirm_params rfile.read failed, ' +
                  str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if '&submitYes=' in follow_confirm_params:
            following_actor = \
                urllib.parse.unquote_plus(follow_confirm_params)
            following_actor = following_actor.split('actor=')[1]
            if '&' in following_actor:
                following_actor = following_actor.split('&')[0]
            following_nickname = get_nickname_from_actor(following_actor)
            following_domain, following_port = \
                get_domain_from_actor(following_actor)
            following_domain_full = \
                get_full_domain(following_domain, following_port)
            if follower_nickname == following_nickname and \
               following_domain == domain and \
               following_port == port:
                if debug:
                    print('You cannot unfollow yourself!')
            else:
                if debug:
                    print(follower_nickname + ' stops following ' +
                          following_actor)
                follow_actor = \
                    local_actor_url(http_prefix,
                                    follower_nickname, domain_full)
                status_number, _ = get_status_number()
                follow_id = follow_actor + '/statuses/' + str(status_number)
                unfollow_json = {
                    '@context': 'https://www.w3.org/ns/activitystreams',
                    'id': follow_id + '/undo',
                    'type': 'Undo',
                    'actor': follow_actor,
                    'object': {
                        'id': follow_id,
                        'type': 'Follow',
                        'actor': follow_actor,
                        'object': following_actor
                    }
                }
                path_users_section = path.split('/users/')[1]
                self.post_to_nickname = path_users_section.split('/')[0]
                group_account = has_group_type(self.server.base_dir,
                                               following_actor,
                                               self.server.person_cache)
                unfollow_account(self.server.base_dir, self.post_to_nickname,
                                 self.server.domain,
                                 following_nickname, following_domain_full,
                                 self.server.debug, group_account)
                self._post_to_outbox_thread(unfollow_json)

        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str = 'http://' + i2p_domain + users_path
        self._redirect_headers(origin_path_str, cookie, calling_domain)
        self.server.postreq_busy = False

    def _follow_confirm(self, calling_domain: str, cookie: str,
                        authorized: bool, path: str,
                        base_dir: str, http_prefix: str,
                        domain: str, domain_full: str, port: int,
                        onion_domain: str, i2p_domain: str,
                        debug: bool) -> None:
        """Confirm to follow
        """
        users_path = path.split('/followconfirm')[0]
        origin_path_str = http_prefix + '://' + domain_full + users_path
        follower_nickname = get_nickname_from_actor(origin_path_str)

        length = int(self.headers['Content-length'])

        try:
            follow_confirm_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST follow_confirm_params ' +
                      'connection was reset')
            else:
                print('EX: POST follow_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST follow_confirm_params rfile.read failed, ' +
                  str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if '&submitView=' in follow_confirm_params:
            following_actor = \
                urllib.parse.unquote_plus(follow_confirm_params)
            following_actor = following_actor.split('actor=')[1]
            if '&' in following_actor:
                following_actor = following_actor.split('&')[0]
            self._redirect_headers(following_actor, cookie, calling_domain)
            self.server.postreq_busy = False
            return

        if '&submitYes=' in follow_confirm_params:
            following_actor = \
                urllib.parse.unquote_plus(follow_confirm_params)
            following_actor = following_actor.split('actor=')[1]
            if '&' in following_actor:
                following_actor = following_actor.split('&')[0]
            following_nickname = get_nickname_from_actor(following_actor)
            following_domain, following_port = \
                get_domain_from_actor(following_actor)
            if follower_nickname == following_nickname and \
               following_domain == domain and \
               following_port == port:
                if debug:
                    print('You cannot follow yourself!')
            elif (following_nickname == 'news' and
                  following_domain == domain and
                  following_port == port):
                if debug:
                    print('You cannot follow the news actor')
            else:
                print('Sending follow request from ' +
                      follower_nickname + ' to ' + following_actor)
                if not self.server.signing_priv_key_pem:
                    print('Sending follow request with no signing key')
                send_follow_request(self.server.session,
                                    base_dir, follower_nickname,
                                    domain, port,
                                    http_prefix,
                                    following_nickname,
                                    following_domain,
                                    following_actor,
                                    following_port, http_prefix,
                                    False, self.server.federation_list,
                                    self.server.send_threads,
                                    self.server.postLog,
                                    self.server.cached_webfingers,
                                    self.server.person_cache, debug,
                                    self.server.project_version,
                                    self.server.signing_priv_key_pem)
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str = 'http://' + i2p_domain + users_path
        self._redirect_headers(origin_path_str, cookie, calling_domain)
        self.server.postreq_busy = False

    def _block_confirm(self, calling_domain: str, cookie: str,
                       authorized: bool, path: str,
                       base_dir: str, http_prefix: str,
                       domain: str, domain_full: str, port: int,
                       onion_domain: str, i2p_domain: str,
                       debug: bool) -> None:
        """Confirms a block
        """
        users_path = path.split('/blockconfirm')[0]
        origin_path_str = http_prefix + '://' + domain_full + users_path
        blocker_nickname = get_nickname_from_actor(origin_path_str)
        if not blocker_nickname:
            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str = 'http://' + onion_domain + users_path
            elif (calling_domain.endswith('.i2p') and i2p_domain):
                origin_path_str = 'http://' + i2p_domain + users_path
            print('WARN: unable to find nickname in ' + origin_path_str)
            self._redirect_headers(origin_path_str,
                                   cookie, calling_domain)
            self.server.postreq_busy = False
            return

        length = int(self.headers['Content-length'])

        try:
            block_confirm_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST block_confirm_params ' +
                      'connection was reset')
            else:
                print('EX: POST block_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST block_confirm_params rfile.read failed, ' +
                  str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if '&submitYes=' in block_confirm_params:
            blocking_actor = \
                urllib.parse.unquote_plus(block_confirm_params)
            blocking_actor = blocking_actor.split('actor=')[1]
            if '&' in blocking_actor:
                blocking_actor = blocking_actor.split('&')[0]
            blocking_nickname = get_nickname_from_actor(blocking_actor)
            if not blocking_nickname:
                if calling_domain.endswith('.onion') and onion_domain:
                    origin_path_str = 'http://' + onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and i2p_domain):
                    origin_path_str = 'http://' + i2p_domain + users_path
                print('WARN: unable to find nickname in ' + blocking_actor)
                self._redirect_headers(origin_path_str,
                                       cookie, calling_domain)
                self.server.postreq_busy = False
                return
            blocking_domain, blocking_port = \
                get_domain_from_actor(blocking_actor)
            blocking_domain_full = \
                get_full_domain(blocking_domain, blocking_port)
            if blocker_nickname == blocking_nickname and \
               blocking_domain == domain and \
               blocking_port == port:
                if debug:
                    print('You cannot block yourself!')
            else:
                print('Adding block by ' + blocker_nickname +
                      ' of ' + blocking_actor)
                if add_block(base_dir, blocker_nickname,
                             domain,
                             blocking_nickname,
                             blocking_domain_full):
                    # send block activity
                    self._send_block(http_prefix,
                                     blocker_nickname, domain_full,
                                     blocking_nickname, blocking_domain_full)
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str = 'http://' + i2p_domain + users_path
        self._redirect_headers(origin_path_str, cookie, calling_domain)
        self.server.postreq_busy = False

    def _unblock_confirm(self, calling_domain: str, cookie: str,
                         authorized: bool, path: str,
                         base_dir: str, http_prefix: str,
                         domain: str, domain_full: str, port: int,
                         onion_domain: str, i2p_domain: str,
                         debug: bool) -> None:
        """Confirms a unblock
        """
        users_path = path.split('/unblockconfirm')[0]
        origin_path_str = http_prefix + '://' + domain_full + users_path
        blocker_nickname = get_nickname_from_actor(origin_path_str)
        if not blocker_nickname:
            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str = 'http://' + onion_domain + users_path
            elif (calling_domain.endswith('.i2p') and i2p_domain):
                origin_path_str = 'http://' + i2p_domain + users_path
            print('WARN: unable to find nickname in ' + origin_path_str)
            self._redirect_headers(origin_path_str,
                                   cookie, calling_domain)
            self.server.postreq_busy = False
            return

        length = int(self.headers['Content-length'])

        try:
            block_confirm_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST block_confirm_params ' +
                      'connection was reset')
            else:
                print('EX: POST block_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST block_confirm_params rfile.read failed, ' +
                  str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if '&submitYes=' in block_confirm_params:
            blocking_actor = \
                urllib.parse.unquote_plus(block_confirm_params)
            blocking_actor = blocking_actor.split('actor=')[1]
            if '&' in blocking_actor:
                blocking_actor = blocking_actor.split('&')[0]
            blocking_nickname = get_nickname_from_actor(blocking_actor)
            if not blocking_nickname:
                if calling_domain.endswith('.onion') and onion_domain:
                    origin_path_str = 'http://' + onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and i2p_domain):
                    origin_path_str = 'http://' + i2p_domain + users_path
                print('WARN: unable to find nickname in ' + blocking_actor)
                self._redirect_headers(origin_path_str,
                                       cookie, calling_domain)
                self.server.postreq_busy = False
                return
            blocking_domain, blocking_port = \
                get_domain_from_actor(blocking_actor)
            blocking_domain_full = \
                get_full_domain(blocking_domain, blocking_port)
            if blocker_nickname == blocking_nickname and \
               blocking_domain == domain and \
               blocking_port == port:
                if debug:
                    print('You cannot unblock yourself!')
            else:
                if debug:
                    print(blocker_nickname + ' stops blocking ' +
                          blocking_actor)
                remove_block(base_dir,
                             blocker_nickname, domain,
                             blocking_nickname, blocking_domain_full)
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str = 'http://' + i2p_domain + users_path
        self._redirect_headers(origin_path_str,
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _receive_search_query(self, calling_domain: str, cookie: str,
                              authorized: bool, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str,
                              port: int, search_for_emoji: bool,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time, getreq_timings: {},
                              debug: bool) -> None:
        """Receive a search query
        """
        # get the page number
        page_number = 1
        if '/searchhandle?page=' in path:
            page_number_str = path.split('/searchhandle?page=')[1]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
            path = path.split('?page=')[0]

        users_path = path.replace('/searchhandle', '')
        actor_str = self._get_instance_url(calling_domain) + users_path
        length = int(self.headers['Content-length'])
        try:
            search_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST search_params connection was reset')
            else:
                print('EX: POST search_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST search_params rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        if 'submitBack=' in search_params:
            # go back on search screen
            self._redirect_headers(actor_str + '/' +
                                   self.server.default_timeline,
                                   cookie, calling_domain)
            self.server.postreq_busy = False
            return
        if 'searchtext=' in search_params:
            search_str = search_params.split('searchtext=')[1]
            if '&' in search_str:
                search_str = search_str.split('&')[0]
            search_str = \
                urllib.parse.unquote_plus(search_str.strip())
            search_str = search_str.lower().strip()
            print('search_str: ' + search_str)
            if search_for_emoji:
                search_str = ':' + search_str + ':'
            if search_str.startswith('#'):
                nickname = get_nickname_from_actor(actor_str)
                # hashtag search
                hashtag_str = \
                    html_hashtag_search(self.server.css_cache,
                                        nickname, domain, port,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        base_dir,
                                        search_str[1:], 1,
                                        MAX_POSTS_IN_HASHTAG_FEED,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        http_prefix,
                                        self.server.project_version,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        self.server.signing_priv_key_pem,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
                if hashtag_str:
                    msg = hashtag_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
            elif (search_str.startswith('*') or
                  search_str.endswith(' skill')):
                possible_endings = (
                    ' skill'
                )
                for poss_ending in possible_endings:
                    if search_str.endswith(poss_ending):
                        search_str = search_str.replace(poss_ending, '')
                        break
                # skill search
                search_str = search_str.replace('*', '').strip()
                skill_str = \
                    html_skills_search(actor_str,
                                       self.server.css_cache,
                                       self.server.translate,
                                       base_dir,
                                       http_prefix,
                                       search_str,
                                       self.server.instance_only_skills_search,
                                       64)
                if skill_str:
                    msg = skill_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
            elif (search_str.startswith("'") or
                  search_str.endswith(' history') or
                  search_str.endswith(' in sent') or
                  search_str.endswith(' in outbox') or
                  search_str.endswith(' in outgoing') or
                  search_str.endswith(' in sent items') or
                  search_str.endswith(' in sent posts') or
                  search_str.endswith(' in outgoing posts') or
                  search_str.endswith(' in my history') or
                  search_str.endswith(' in my outbox') or
                  search_str.endswith(' in my posts')):
                possible_endings = (
                    ' in my posts',
                    ' in my history',
                    ' in my outbox',
                    ' in sent posts',
                    ' in outgoing posts',
                    ' in sent items',
                    ' in history',
                    ' in outbox',
                    ' in outgoing',
                    ' in sent',
                    ' history'
                )
                for poss_ending in possible_endings:
                    if search_str.endswith(poss_ending):
                        search_str = search_str.replace(poss_ending, '')
                        break
                # your post history search
                nickname = get_nickname_from_actor(actor_str)
                search_str = search_str.replace("'", '', 1).strip()
                history_str = \
                    html_history_search(self.server.css_cache,
                                        self.server.translate,
                                        base_dir,
                                        http_prefix,
                                        nickname,
                                        domain,
                                        search_str,
                                        MAX_POSTS_IN_FEED,
                                        page_number,
                                        self.server.project_version,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        port,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name, 'outbox',
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        self.server.signing_priv_key_pem,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
                if history_str:
                    msg = history_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
            elif (search_str.startswith('-') or
                  search_str.endswith(' in my saved items') or
                  search_str.endswith(' in my saved posts') or
                  search_str.endswith(' in my bookmarks') or
                  search_str.endswith(' in my saved') or
                  search_str.endswith(' in my saves') or
                  search_str.endswith(' in saved posts') or
                  search_str.endswith(' in saved items') or
                  search_str.endswith(' in bookmarks') or
                  search_str.endswith(' in saved') or
                  search_str.endswith(' in saves') or
                  search_str.endswith(' bookmark')):
                possible_endings = (
                    ' in my bookmarks'
                    ' in my saved posts'
                    ' in my saved items'
                    ' in my saved'
                    ' in my saves'
                    ' in saved posts'
                    ' in saved items'
                    ' in saved'
                    ' in saves'
                    ' in bookmarks'
                    ' bookmark'
                )
                for poss_ending in possible_endings:
                    if search_str.endswith(poss_ending):
                        search_str = search_str.replace(poss_ending, '')
                        break
                # bookmark search
                nickname = get_nickname_from_actor(actor_str)
                search_str = search_str.replace('-', '', 1).strip()
                bookmarks_str = \
                    html_history_search(self.server.css_cache,
                                        self.server.translate,
                                        base_dir,
                                        http_prefix,
                                        nickname,
                                        domain,
                                        search_str,
                                        MAX_POSTS_IN_FEED,
                                        page_number,
                                        self.server.project_version,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        port,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name, 'bookmarks',
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        self.server.signing_priv_key_pem,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
                if bookmarks_str:
                    msg = bookmarks_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
            elif ('@' in search_str or
                  ('://' in search_str and
                   has_users_path(search_str))):
                if search_str.endswith(':') or \
                   search_str.endswith(';') or \
                   search_str.endswith('.'):
                    actor_str = \
                        self._get_instance_url(calling_domain) + users_path
                    self._redirect_headers(actor_str + '/search',
                                           cookie, calling_domain)
                    self.server.postreq_busy = False
                    return
                # profile search
                nickname = get_nickname_from_actor(actor_str)
                if not self._establish_session("handle search"):
                    self.server.postreq_busy = False
                    return
                profile_path_str = path.replace('/searchhandle', '')

                # are we already following the searched for handle?
                if is_following_actor(base_dir, nickname, domain, search_str):
                    if not has_users_path(search_str):
                        search_nickname = get_nickname_from_actor(search_str)
                        search_domain, search_port = \
                            get_domain_from_actor(search_str)
                        search_domain_full = \
                            get_full_domain(search_domain, search_port)
                        actor = \
                            local_actor_url(http_prefix, search_nickname,
                                            search_domain_full)
                    else:
                        actor = search_str
                    avatar_url = \
                        get_avatar_image_url(self.server.session,
                                             base_dir, http_prefix,
                                             actor,
                                             self.server.person_cache,
                                             None, True,
                                             self.server.signing_priv_key_pem)
                    profile_path_str += \
                        '?options=' + actor + ';1;' + avatar_url

                    self._show_person_options(calling_domain, profile_path_str,
                                              base_dir, http_prefix,
                                              domain, domain_full,
                                              getreq_start_time,
                                              onion_domain, i2p_domain,
                                              cookie, debug, authorized)
                    return
                else:
                    show_published_date_only = \
                        self.server.show_published_date_only
                    allow_local_network_access = \
                        self.server.allow_local_network_access

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = self.server.key_shortcuts[nickname]

                    signing_priv_key_pem = \
                        self.server.signing_priv_key_pem
                    twitter_replacement_domain = \
                        self.server.twitter_replacement_domain
                    peertube_instances = \
                        self.server.peertube_instances
                    yt_replace_domain = \
                        self.server.yt_replace_domain
                    cached_webfingers = \
                        self.server.cached_webfingers
                    recent_posts_cache = \
                        self.server.recent_posts_cache
                    profile_str = \
                        html_profile_after_search(self.server.css_cache,
                                                  recent_posts_cache,
                                                  self.server.max_recent_posts,
                                                  self.server.translate,
                                                  base_dir,
                                                  profile_path_str,
                                                  http_prefix,
                                                  nickname,
                                                  domain,
                                                  port,
                                                  search_str,
                                                  self.server.session,
                                                  cached_webfingers,
                                                  self.server.person_cache,
                                                  self.server.debug,
                                                  self.server.project_version,
                                                  yt_replace_domain,
                                                  twitter_replacement_domain,
                                                  show_published_date_only,
                                                  self.server.default_timeline,
                                                  peertube_instances,
                                                  allow_local_network_access,
                                                  self.server.theme_name,
                                                  access_keys,
                                                  self.server.system_language,
                                                  self.server.max_like_count,
                                                  signing_priv_key_pem,
                                                  self.server.cw_lists,
                                                  self.server.lists_enabled)
                if profile_str:
                    msg = profile_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
                else:
                    actor_str = \
                        self._get_instance_url(calling_domain) + users_path
                    self._redirect_headers(actor_str + '/search',
                                           cookie, calling_domain)
                    self.server.postreq_busy = False
                    return
            elif (search_str.startswith(':') or
                  search_str.endswith(' emoji')):
                # eg. "cat emoji"
                if search_str.endswith(' emoji'):
                    search_str = \
                        search_str.replace(' emoji', '')
                # emoji search
                emoji_str = \
                    html_search_emoji(self.server.css_cache,
                                      self.server.translate,
                                      base_dir,
                                      http_prefix,
                                      search_str)
                if emoji_str:
                    msg = emoji_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
            elif search_str.startswith('.'):
                # wanted items search
                shared_items_federated_domains = \
                    self.server.shared_items_federated_domains
                wanted_items_str = \
                    html_search_shared_items(self.server.css_cache,
                                             self.server.translate,
                                             base_dir,
                                             search_str[1:], page_number,
                                             MAX_POSTS_IN_FEED,
                                             http_prefix,
                                             domain_full,
                                             actor_str, calling_domain,
                                             shared_items_federated_domains,
                                             'wanted')
                if wanted_items_str:
                    msg = wanted_items_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
            else:
                # shared items search
                shared_items_federated_domains = \
                    self.server.shared_items_federated_domains
                shared_items_str = \
                    html_search_shared_items(self.server.css_cache,
                                             self.server.translate,
                                             base_dir,
                                             search_str, page_number,
                                             MAX_POSTS_IN_FEED,
                                             http_prefix,
                                             domain_full,
                                             actor_str, calling_domain,
                                             shared_items_federated_domains,
                                             'shares')
                if shared_items_str:
                    msg = shared_items_str.encode('utf-8')
                    msglen = len(msg)
                    self._login_headers('text/html',
                                        msglen, calling_domain)
                    self._write(msg)
                    self.server.postreq_busy = False
                    return
        actor_str = self._get_instance_url(calling_domain) + users_path
        self._redirect_headers(actor_str + '/' +
                               self.server.default_timeline,
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _receive_vote(self, calling_domain: str, cookie: str,
                      authorized: bool, path: str,
                      base_dir: str, http_prefix: str,
                      domain: str, domain_full: str,
                      onion_domain: str, i2p_domain: str,
                      debug: bool) -> None:
        """Receive a vote via POST
        """
        page_number = 1
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
            path = path.split('?page=')[0]

        # the actor who votes
        users_path = path.replace('/question', '')
        actor = http_prefix + '://' + domain_full + users_path
        nickname = get_nickname_from_actor(actor)
        if not nickname:
            if calling_domain.endswith('.onion') and onion_domain:
                actor = 'http://' + onion_domain + users_path
            elif (calling_domain.endswith('.i2p') and i2p_domain):
                actor = 'http://' + i2p_domain + users_path
            actor_path_str = \
                actor + '/' + self.server.default_timeline + \
                '?page=' + str(page_number)
            self._redirect_headers(actor_path_str,
                                   cookie, calling_domain)
            self.server.postreq_busy = False
            return

        # get the parameters
        length = int(self.headers['Content-length'])

        try:
            question_params = self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST question_params connection was reset')
            else:
                print('EX: POST question_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST question_params rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        question_params = question_params.replace('+', ' ')
        question_params = question_params.replace('%3F', '')
        question_params = \
            urllib.parse.unquote_plus(question_params.strip())

        # post being voted on
        message_id = None
        if 'messageId=' in question_params:
            message_id = question_params.split('messageId=')[1]
            if '&' in message_id:
                message_id = message_id.split('&')[0]

        answer = None
        if 'answer=' in question_params:
            answer = question_params.split('answer=')[1]
            if '&' in answer:
                answer = answer.split('&')[0]

        self._send_reply_to_question(nickname, message_id, answer)
        if calling_domain.endswith('.onion') and onion_domain:
            actor = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            actor = 'http://' + i2p_domain + users_path
        actor_path_str = \
            actor + '/' + self.server.default_timeline + \
            '?page=' + str(page_number)
        self._redirect_headers(actor_path_str, cookie,
                               calling_domain)
        self.server.postreq_busy = False
        return

    def _receive_image(self, length: int,
                       calling_domain: str, cookie: str,
                       authorized: bool, path: str,
                       base_dir: str, http_prefix: str,
                       domain: str, domain_full: str,
                       onion_domain: str, i2p_domain: str,
                       debug: bool) -> None:
        """Receives an image via POST
        """
        if not self.outbox_authenticated:
            if debug:
                print('DEBUG: unauthenticated attempt to ' +
                      'post image to outbox')
            self.send_response(403)
            self.end_headers()
            self.server.postreq_busy = False
            return
        path_users_section = path.split('/users/')[1]
        if '/' not in path_users_section:
            self._404()
            self.server.postreq_busy = False
            return
        self.post_from_nickname = path_users_section.split('/')[0]
        accounts_dir = acct_dir(base_dir, self.post_from_nickname, domain)
        if not os.path.isdir(accounts_dir):
            self._404()
            self.server.postreq_busy = False
            return

        try:
            media_bytes = self.rfile.read(length)
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST media_bytes ' +
                      'connection reset by peer')
            else:
                print('EX: POST media_bytes socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST media_bytes rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        media_filename_base = accounts_dir + '/upload'
        media_filename = \
            media_filename_base + '.' + \
            get_image_extension_from_mime_type(self.headers['Content-type'])
        try:
            with open(media_filename, 'wb') as av_file:
                av_file.write(media_bytes)
        except OSError:
            print('EX: unable to write ' + media_filename)
        if debug:
            print('DEBUG: image saved to ' + media_filename)
        self.send_response(201)
        self.end_headers()
        self.server.postreq_busy = False

    def _remove_share(self, calling_domain: str, cookie: str,
                      authorized: bool, path: str,
                      base_dir: str, http_prefix: str,
                      domain: str, domain_full: str,
                      onion_domain: str, i2p_domain: str,
                      debug: bool) -> None:
        """Removes a shared item
        """
        users_path = path.split('/rmshare')[0]
        origin_path_str = http_prefix + '://' + domain_full + users_path

        length = int(self.headers['Content-length'])

        try:
            remove_share_confirm_params = \
                self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST remove_share_confirm_params ' +
                      'connection was reset')
            else:
                print('EX: POST remove_share_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST remove_share_confirm_params ' +
                  'rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if '&submitYes=' in remove_share_confirm_params and authorized:
            remove_share_confirm_params = \
                remove_share_confirm_params.replace('+', ' ').strip()
            remove_share_confirm_params = \
                urllib.parse.unquote_plus(remove_share_confirm_params)
            share_actor = remove_share_confirm_params.split('actor=')[1]
            if '&' in share_actor:
                share_actor = share_actor.split('&')[0]
            admin_nickname = get_config_param(base_dir, 'admin')
            admin_actor = \
                local_actor_url(http_prefix, admin_nickname, domain_full)
            actor = origin_path_str
            actor_nickname = get_nickname_from_actor(actor)
            if actor == share_actor or actor == admin_actor or \
               is_moderator(base_dir, actor_nickname):
                item_id = remove_share_confirm_params.split('itemID=')[1]
                if '&' in item_id:
                    item_id = item_id.split('&')[0]
                share_nickname = get_nickname_from_actor(share_actor)
                if share_nickname:
                    share_domain, _ = \
                        get_domain_from_actor(share_actor)
                    remove_shared_item(base_dir,
                                       share_nickname, share_domain, item_id,
                                       http_prefix, domain_full, 'shares')

        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str = 'http://' + i2p_domain + users_path
        self._redirect_headers(origin_path_str + '/tlshares',
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _remove_wanted(self, calling_domain: str, cookie: str,
                       authorized: bool, path: str,
                       base_dir: str, http_prefix: str,
                       domain: str, domain_full: str,
                       onion_domain: str, i2p_domain: str,
                       debug: bool) -> None:
        """Removes a wanted item
        """
        users_path = path.split('/rmwanted')[0]
        origin_path_str = http_prefix + '://' + domain_full + users_path

        length = int(self.headers['Content-length'])

        try:
            remove_share_confirm_params = \
                self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST remove_share_confirm_params ' +
                      'connection was reset')
            else:
                print('EX: POST remove_share_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST remove_share_confirm_params ' +
                  'rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if '&submitYes=' in remove_share_confirm_params and authorized:
            remove_share_confirm_params = \
                remove_share_confirm_params.replace('+', ' ').strip()
            remove_share_confirm_params = \
                urllib.parse.unquote_plus(remove_share_confirm_params)
            share_actor = remove_share_confirm_params.split('actor=')[1]
            if '&' in share_actor:
                share_actor = share_actor.split('&')[0]
            admin_nickname = get_config_param(base_dir, 'admin')
            admin_actor = \
                local_actor_url(http_prefix, admin_nickname, domain_full)
            actor = origin_path_str
            actor_nickname = get_nickname_from_actor(actor)
            if actor == share_actor or actor == admin_actor or \
               is_moderator(base_dir, actor_nickname):
                item_id = remove_share_confirm_params.split('itemID=')[1]
                if '&' in item_id:
                    item_id = item_id.split('&')[0]
                share_nickname = get_nickname_from_actor(share_actor)
                if share_nickname:
                    share_domain, _ = \
                        get_domain_from_actor(share_actor)
                    remove_shared_item(base_dir,
                                       share_nickname, share_domain, item_id,
                                       http_prefix, domain_full, 'wanted')

        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str = 'http://' + i2p_domain + users_path
        self._redirect_headers(origin_path_str + '/tlwanted',
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _receive_remove_post(self, calling_domain: str, cookie: str,
                             authorized: bool, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str,
                             onion_domain: str, i2p_domain: str,
                             debug: bool) -> None:
        """Endpoint for removing posts after confirmation
        """
        page_number = 1
        users_path = path.split('/rmpost')[0]
        origin_path_str = \
            http_prefix + '://' + \
            domain_full + users_path

        length = int(self.headers['Content-length'])

        try:
            remove_post_confirm_params = \
                self.rfile.read(length).decode('utf-8')
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('EX: POST remove_post_confirm_params ' +
                      'connection was reset')
            else:
                print('EX: POST remove_post_confirm_params socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST remove_post_confirm_params ' +
                  'rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        if '&submitYes=' in remove_post_confirm_params:
            remove_post_confirm_params = \
                urllib.parse.unquote_plus(remove_post_confirm_params)
            remove_message_id = \
                remove_post_confirm_params.split('messageId=')[1]
            if '&' in remove_message_id:
                remove_message_id = remove_message_id.split('&')[0]
            if 'pageNumber=' in remove_post_confirm_params:
                page_number_str = \
                    remove_post_confirm_params.split('pageNumber=')[1]
                if '&' in page_number_str:
                    page_number_str = page_number_str.split('&')[0]
                if page_number_str.isdigit():
                    page_number = int(page_number_str)
            year_str = None
            if 'year=' in remove_post_confirm_params:
                year_str = remove_post_confirm_params.split('year=')[1]
                if '&' in year_str:
                    year_str = year_str.split('&')[0]
            month_str = None
            if 'month=' in remove_post_confirm_params:
                month_str = remove_post_confirm_params.split('month=')[1]
                if '&' in month_str:
                    month_str = month_str.split('&')[0]
            if '/statuses/' in remove_message_id:
                remove_post_actor = remove_message_id.split('/statuses/')[0]
            if origin_path_str in remove_post_actor:
                toList = ['https://www.w3.org/ns/activitystreams#Public',
                          remove_post_actor]
                delete_json = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    'actor': remove_post_actor,
                    'object': remove_message_id,
                    'to': toList,
                    'cc': [remove_post_actor + '/followers'],
                    'type': 'Delete'
                }
                self.post_to_nickname = \
                    get_nickname_from_actor(remove_post_actor)
                if self.post_to_nickname:
                    if month_str and year_str:
                        if month_str.isdigit() and year_str.isdigit():
                            year_int = int(year_str)
                            month_int = int(month_str)
                            remove_calendar_event(base_dir,
                                                  self.post_to_nickname,
                                                  domain, year_int,
                                                  month_int,
                                                  remove_message_id)
                    self._post_to_outbox_thread(delete_json)
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str = 'http://' + i2p_domain + users_path
        if page_number == 1:
            self._redirect_headers(origin_path_str + '/outbox', cookie,
                                   calling_domain)
        else:
            page_number_str = str(page_number)
            actor_path_str = \
                origin_path_str + '/outbox?page=' + page_number_str
            self._redirect_headers(actor_path_str,
                                   cookie, calling_domain)
        self.server.postreq_busy = False

    def _links_update(self, calling_domain: str, cookie: str,
                      authorized: bool, path: str,
                      base_dir: str, http_prefix: str,
                      domain: str, domain_full: str,
                      onion_domain: str, i2p_domain: str, debug: bool,
                      default_timeline: str,
                      allow_local_network_access: bool) -> None:
        """Updates the left links column of the timeline
        """
        users_path = path.replace('/linksdata', '')
        users_path = users_path.replace('/editlinks', '')
        actor_str = self._get_instance_url(calling_domain) + users_path
        if ' boundary=' in self.headers['Content-type']:
            boundary = self.headers['Content-type'].split('boundary=')[1]
            if ';' in boundary:
                boundary = boundary.split(';')[0]

            # get the nickname
            nickname = get_nickname_from_actor(actor_str)
            editor = None
            if nickname:
                editor = is_editor(base_dir, nickname)
            if not nickname or not editor:
                if not nickname:
                    print('WARN: nickname not found in ' + actor_str)
                else:
                    print('WARN: nickname is not a moderator' + actor_str)
                self._redirect_headers(actor_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            length = int(self.headers['Content-length'])

            # check that the POST isn't too large
            if length > self.server.max_post_length:
                print('Maximum links data length exceeded ' + str(length))
                self._redirect_headers(actor_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            try:
                # read the bytes of the http form POST
                post_bytes = self.rfile.read(length)
            except SocketError as ex:
                if ex.errno == errno.ECONNRESET:
                    print('EX: connection was reset while ' +
                          'reading bytes from http form POST')
                else:
                    print('EX: error while reading bytes ' +
                          'from http form POST')
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return
            except ValueError as ex:
                print('EX: failed to read bytes for POST, ' + str(ex))
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return

            links_filename = base_dir + '/accounts/links.txt'
            about_filename = base_dir + '/accounts/about.md'
            tos_filename = base_dir + '/accounts/tos.md'

            # extract all of the text fields into a dict
            fields = \
                extract_text_fields_in_post(post_bytes, boundary, debug)

            if fields.get('editedLinks'):
                links_str = fields['editedLinks']
                if fields.get('newColLink'):
                    if links_str:
                        if not links_str.endswith('\n'):
                            links_str += '\n'
                    links_str += fields['newColLink'] + '\n'
                try:
                    with open(links_filename, 'w+') as linksfile:
                        linksfile.write(links_str)
                except OSError:
                    print('EX: _links_update unable to write ' +
                          links_filename)
            else:
                if fields.get('newColLink'):
                    # the text area is empty but there is a new link added
                    links_str = fields['newColLink'] + '\n'
                    try:
                        with open(links_filename, 'w+') as linksfile:
                            linksfile.write(links_str)
                    except OSError:
                        print('EX: _links_update unable to write ' +
                              links_filename)
                else:
                    if os.path.isfile(links_filename):
                        try:
                            os.remove(links_filename)
                        except OSError:
                            print('EX: _links_update unable to delete ' +
                                  links_filename)

            admin_nickname = \
                get_config_param(base_dir, 'admin')
            if nickname == admin_nickname:
                if fields.get('editedAbout'):
                    about_str = fields['editedAbout']
                    if not dangerous_markup(about_str,
                                            allow_local_network_access):
                        try:
                            with open(about_filename, 'w+') as aboutfile:
                                aboutfile.write(about_str)
                        except OSError:
                            print('EX: unable to write about ' +
                                  about_filename)
                else:
                    if os.path.isfile(about_filename):
                        try:
                            os.remove(about_filename)
                        except OSError:
                            print('EX: _links_update unable to delete ' +
                                  about_filename)

                if fields.get('editedTOS'):
                    tos_str = fields['editedTOS']
                    if not dangerous_markup(tos_str,
                                            allow_local_network_access):
                        try:
                            with open(tos_filename, 'w+') as tosfile:
                                tosfile.write(tos_str)
                        except OSError:
                            print('EX: unable to write TOS ' + tos_filename)
                else:
                    if os.path.isfile(tos_filename):
                        try:
                            os.remove(tos_filename)
                        except OSError:
                            print('EX: _links_update unable to delete ' +
                                  tos_filename)

        # redirect back to the default timeline
        self._redirect_headers(actor_str + '/' + default_timeline,
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _set_hashtag_category(self, calling_domain: str, cookie: str,
                              authorized: bool, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str,
                              onion_domain: str, i2p_domain: str, debug: bool,
                              default_timeline: str,
                              allow_local_network_access: bool) -> None:
        """On the screen after selecting a hashtag from the swarm, this sets
        the category for that tag
        """
        users_path = path.replace('/sethashtagcategory', '')
        hashtag = ''
        if '/tags/' not in users_path:
            # no hashtag is specified within the path
            self._404()
            return
        hashtag = users_path.split('/tags/')[1].strip()
        hashtag = urllib.parse.unquote_plus(hashtag)
        if not hashtag:
            # no hashtag was given in the path
            self._404()
            return
        hashtag_filename = base_dir + '/tags/' + hashtag + '.txt'
        if not os.path.isfile(hashtag_filename):
            # the hashtag does not exist
            self._404()
            return
        users_path = users_path.split('/tags/')[0]
        actor_str = self._get_instance_url(calling_domain) + users_path
        tag_screen_str = actor_str + '/tags/' + hashtag
        if ' boundary=' in self.headers['Content-type']:
            boundary = self.headers['Content-type'].split('boundary=')[1]
            if ';' in boundary:
                boundary = boundary.split(';')[0]

            # get the nickname
            nickname = get_nickname_from_actor(actor_str)
            editor = None
            if nickname:
                editor = is_editor(base_dir, nickname)
            if not hashtag or not editor:
                if not nickname:
                    print('WARN: nickname not found in ' + actor_str)
                else:
                    print('WARN: nickname is not a moderator' + actor_str)
                self._redirect_headers(tag_screen_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            length = int(self.headers['Content-length'])

            # check that the POST isn't too large
            if length > self.server.max_post_length:
                print('Maximum links data length exceeded ' + str(length))
                self._redirect_headers(tag_screen_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            try:
                # read the bytes of the http form POST
                post_bytes = self.rfile.read(length)
            except SocketError as ex:
                if ex.errno == errno.ECONNRESET:
                    print('EX: connection was reset while ' +
                          'reading bytes from http form POST')
                else:
                    print('EX: error while reading bytes ' +
                          'from http form POST')
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return
            except ValueError as ex:
                print('EX: failed to read bytes for POST, ' + str(ex))
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return

            # extract all of the text fields into a dict
            fields = \
                extract_text_fields_in_post(post_bytes, boundary, debug)

            if fields.get('hashtagCategory'):
                category_str = fields['hashtagCategory'].lower()
                if not is_blocked_hashtag(base_dir, category_str) and \
                   not is_filtered(base_dir, nickname, domain, category_str):
                    set_hashtag_category(base_dir, hashtag,
                                         category_str, False)
            else:
                category_filename = base_dir + '/tags/' + hashtag + '.category'
                if os.path.isfile(category_filename):
                    try:
                        os.remove(category_filename)
                    except OSError:
                        print('EX: _set_hashtag_category unable to delete ' +
                              category_filename)

        # redirect back to the default timeline
        self._redirect_headers(tag_screen_str,
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _newswire_update(self, calling_domain: str, cookie: str,
                         authorized: bool, path: str,
                         base_dir: str, http_prefix: str,
                         domain: str, domain_full: str,
                         onion_domain: str, i2p_domain: str, debug: bool,
                         default_timeline: str) -> None:
        """Updates the right newswire column of the timeline
        """
        users_path = path.replace('/newswiredata', '')
        users_path = users_path.replace('/editnewswire', '')
        actor_str = self._get_instance_url(calling_domain) + users_path
        if ' boundary=' in self.headers['Content-type']:
            boundary = self.headers['Content-type'].split('boundary=')[1]
            if ';' in boundary:
                boundary = boundary.split(';')[0]

            # get the nickname
            nickname = get_nickname_from_actor(actor_str)
            moderator = None
            if nickname:
                moderator = is_moderator(base_dir, nickname)
            if not nickname or not moderator:
                if not nickname:
                    print('WARN: nickname not found in ' + actor_str)
                else:
                    print('WARN: nickname is not a moderator' + actor_str)
                self._redirect_headers(actor_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            length = int(self.headers['Content-length'])

            # check that the POST isn't too large
            if length > self.server.max_post_length:
                print('Maximum newswire data length exceeded ' + str(length))
                self._redirect_headers(actor_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            try:
                # read the bytes of the http form POST
                post_bytes = self.rfile.read(length)
            except SocketError as ex:
                if ex.errno == errno.ECONNRESET:
                    print('EX: connection was reset while ' +
                          'reading bytes from http form POST')
                else:
                    print('EX: error while reading bytes ' +
                          'from http form POST')
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return
            except ValueError as ex:
                print('EX: failed to read bytes for POST, ' + str(ex))
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return

            newswire_filename = base_dir + '/accounts/newswire.txt'

            # extract all of the text fields into a dict
            fields = \
                extract_text_fields_in_post(post_bytes, boundary, debug)
            if fields.get('editedNewswire'):
                newswire_str = fields['editedNewswire']
                # append a new newswire entry
                if fields.get('newNewswireFeed'):
                    if newswire_str:
                        if not newswire_str.endswith('\n'):
                            newswire_str += '\n'
                    newswire_str += fields['newNewswireFeed'] + '\n'
                try:
                    with open(newswire_filename, 'w+') as newsfile:
                        newsfile.write(newswire_str)
                except OSError:
                    print('EX: unable to write ' + newswire_filename)
            else:
                if fields.get('newNewswireFeed'):
                    # the text area is empty but there is a new feed added
                    newswire_str = fields['newNewswireFeed'] + '\n'
                    try:
                        with open(newswire_filename, 'w+') as newsfile:
                            newsfile.write(newswire_str)
                    except OSError:
                        print('EX: unable to write ' + newswire_filename)
                else:
                    # text area has been cleared and there is no new feed
                    if os.path.isfile(newswire_filename):
                        try:
                            os.remove(newswire_filename)
                        except OSError:
                            print('EX: _newswire_update unable to delete ' +
                                  newswire_filename)

            # save filtered words list for the newswire
            filter_newswire_filename = \
                base_dir + '/accounts/' + \
                'news@' + domain + '/filters.txt'
            if fields.get('filteredWordsNewswire'):
                try:
                    with open(filter_newswire_filename, 'w+') as filterfile:
                        filterfile.write(fields['filteredWordsNewswire'])
                except OSError:
                    print('EX: unable to write ' + filter_newswire_filename)
            else:
                if os.path.isfile(filter_newswire_filename):
                    try:
                        os.remove(filter_newswire_filename)
                    except OSError:
                        print('EX: _newswire_update unable to delete ' +
                              filter_newswire_filename)

            # save news tagging rules
            hashtag_rules_filename = \
                base_dir + '/accounts/hashtagrules.txt'
            if fields.get('hashtagRulesList'):
                try:
                    with open(hashtag_rules_filename, 'w+') as rulesfile:
                        rulesfile.write(fields['hashtagRulesList'])
                except OSError:
                    print('EX: unable to write ' + hashtag_rules_filename)
            else:
                if os.path.isfile(hashtag_rules_filename):
                    try:
                        os.remove(hashtag_rules_filename)
                    except OSError:
                        print('EX: _newswire_update unable to delete ' +
                              hashtag_rules_filename)

            newswire_tusted_filename = \
                base_dir + '/accounts/newswiretrusted.txt'
            if fields.get('trustedNewswire'):
                newswire_trusted = fields['trustedNewswire']
                if not newswire_trusted.endswith('\n'):
                    newswire_trusted += '\n'
                try:
                    with open(newswire_tusted_filename, 'w+') as trustfile:
                        trustfile.write(newswire_trusted)
                except OSError:
                    print('EX: unable to write ' + newswire_tusted_filename)
            else:
                if os.path.isfile(newswire_tusted_filename):
                    try:
                        os.remove(newswire_tusted_filename)
                    except OSError:
                        print('EX: _newswire_update unable to delete ' +
                              newswire_tusted_filename)

        # redirect back to the default timeline
        self._redirect_headers(actor_str + '/' + default_timeline,
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _citations_update(self, calling_domain: str, cookie: str,
                          authorized: bool, path: str,
                          base_dir: str, http_prefix: str,
                          domain: str, domain_full: str,
                          onion_domain: str, i2p_domain: str, debug: bool,
                          default_timeline: str,
                          newswire: {}) -> None:
        """Updates the citations for a blog post after hitting
        update button on the citations screen
        """
        users_path = path.replace('/citationsdata', '')
        actor_str = self._get_instance_url(calling_domain) + users_path
        nickname = get_nickname_from_actor(actor_str)

        citations_filename = \
            acct_dir(base_dir, nickname, domain) + '/.citations.txt'
        # remove any existing citations file
        if os.path.isfile(citations_filename):
            try:
                os.remove(citations_filename)
            except OSError:
                print('EX: _citations_update unable to delete ' +
                      citations_filename)

        if newswire and \
           ' boundary=' in self.headers['Content-type']:
            boundary = self.headers['Content-type'].split('boundary=')[1]
            if ';' in boundary:
                boundary = boundary.split(';')[0]

            length = int(self.headers['Content-length'])

            # check that the POST isn't too large
            if length > self.server.max_post_length:
                print('Maximum citations data length exceeded ' + str(length))
                self._redirect_headers(actor_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            try:
                # read the bytes of the http form POST
                post_bytes = self.rfile.read(length)
            except SocketError as ex:
                if ex.errno == errno.ECONNRESET:
                    print('EX: connection was reset while ' +
                          'reading bytes from http form ' +
                          'citation screen POST')
                else:
                    print('EX: error while reading bytes ' +
                          'from http form citations screen POST')
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return
            except ValueError as ex:
                print('EX: failed to read bytes for ' +
                      'citations screen POST, ' + str(ex))
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return

            # extract all of the text fields into a dict
            fields = \
                extract_text_fields_in_post(post_bytes, boundary, debug)
            print('citationstest: ' + str(fields))
            citations = []
            for ctr in range(0, 128):
                field_name = 'newswire' + str(ctr)
                if not fields.get(field_name):
                    continue
                citations.append(fields[field_name])

            if citations:
                citations_str = ''
                for citation_date in citations:
                    citations_str += citation_date + '\n'
                # save citations dates, so that they can be added when
                # reloading the newblog screen
                try:
                    with open(citations_filename, 'w+') as citfile:
                        citfile.write(citations_str)
                except OSError:
                    print('EX: unable to write ' + citations_filename)

        # redirect back to the default timeline
        self._redirect_headers(actor_str + '/newblog',
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _news_post_edit(self, calling_domain: str, cookie: str,
                        authorized: bool, path: str,
                        base_dir: str, http_prefix: str,
                        domain: str, domain_full: str,
                        onion_domain: str, i2p_domain: str, debug: bool,
                        default_timeline: str) -> None:
        """edits a news post after receiving POST
        """
        users_path = path.replace('/newseditdata', '')
        users_path = users_path.replace('/editnewspost', '')
        actor_str = self._get_instance_url(calling_domain) + users_path
        if ' boundary=' in self.headers['Content-type']:
            boundary = self.headers['Content-type'].split('boundary=')[1]
            if ';' in boundary:
                boundary = boundary.split(';')[0]

            # get the nickname
            nickname = get_nickname_from_actor(actor_str)
            editor_role = None
            if nickname:
                editor_role = is_editor(base_dir, nickname)
            if not nickname or not editor_role:
                if not nickname:
                    print('WARN: nickname not found in ' + actor_str)
                else:
                    print('WARN: nickname is not an editor' + actor_str)
                if self.server.news_instance:
                    self._redirect_headers(actor_str + '/tlfeatures',
                                           cookie, calling_domain)
                else:
                    self._redirect_headers(actor_str + '/tlnews',
                                           cookie, calling_domain)
                self.server.postreq_busy = False
                return

            length = int(self.headers['Content-length'])

            # check that the POST isn't too large
            if length > self.server.max_post_length:
                print('Maximum news data length exceeded ' + str(length))
                if self.server.news_instance:
                    self._redirect_headers(actor_str + '/tlfeatures',
                                           cookie, calling_domain)
                else:
                    self._redirect_headers(actor_str + '/tlnews',
                                           cookie, calling_domain)
                self.server.postreq_busy = False
                return

            try:
                # read the bytes of the http form POST
                post_bytes = self.rfile.read(length)
            except SocketError as ex:
                if ex.errno == errno.ECONNRESET:
                    print('EX: connection was reset while ' +
                          'reading bytes from http form POST')
                else:
                    print('EX: error while reading bytes ' +
                          'from http form POST')
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return
            except ValueError as ex:
                print('EX: failed to read bytes for POST, ' + str(ex))
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return

            # extract all of the text fields into a dict
            fields = \
                extract_text_fields_in_post(post_bytes, boundary, debug)
            news_post_url = None
            news_post_title = None
            news_post_content = None
            if fields.get('newsPostUrl'):
                news_post_url = fields['newsPostUrl']
            if fields.get('newsPostTitle'):
                news_post_title = fields['newsPostTitle']
            if fields.get('editedNewsPost'):
                news_post_content = fields['editedNewsPost']

            if news_post_url and news_post_content and news_post_title:
                # load the post
                post_filename = \
                    locate_post(base_dir, nickname, domain,
                                news_post_url)
                if post_filename:
                    post_json_object = load_json(post_filename)
                    # update the content and title
                    post_json_object['object']['summary'] = \
                        news_post_title
                    post_json_object['object']['content'] = \
                        news_post_content
                    content_map = post_json_object['object']['contentMap']
                    content_map[self.server.system_language] = \
                        news_post_content
                    # update newswire
                    pub_date = post_json_object['object']['published']
                    published_date = \
                        datetime.datetime.strptime(pub_date,
                                                   "%Y-%m-%dT%H:%M:%SZ")
                    if self.server.newswire.get(str(published_date)):
                        self.server.newswire[published_date][0] = \
                            news_post_title
                        self.server.newswire[published_date][4] = \
                            first_paragraph_from_string(news_post_content)
                        # save newswire
                        newswire_state_filename = \
                            base_dir + '/accounts/.newswirestate.json'
                        try:
                            save_json(self.server.newswire,
                                      newswire_state_filename)
                        except BaseException as ex:
                            print('EX: saving newswire state, ' + str(ex))

                    # remove any previous cached news posts
                    news_id = \
                        remove_id_ending(post_json_object['object']['id'])
                    news_id = news_id.replace('/', '#')
                    clear_from_post_caches(base_dir,
                                           self.server.recent_posts_cache,
                                           news_id)

                    # save the news post
                    save_json(post_json_object, post_filename)

        # redirect back to the default timeline
        if self.server.news_instance:
            self._redirect_headers(actor_str + '/tlfeatures',
                                   cookie, calling_domain)
        else:
            self._redirect_headers(actor_str + '/tlnews',
                                   cookie, calling_domain)
        self.server.postreq_busy = False

    def _profile_edit(self, calling_domain: str, cookie: str,
                      authorized: bool, path: str,
                      base_dir: str, http_prefix: str,
                      domain: str, domain_full: str,
                      onion_domain: str, i2p_domain: str,
                      debug: bool, allow_local_network_access: bool,
                      system_language: str,
                      content_license_url: str) -> None:
        """Updates your user profile after editing via the Edit button
        on the profile screen
        """
        users_path = path.replace('/profiledata', '')
        users_path = users_path.replace('/editprofile', '')
        actor_str = self._get_instance_url(calling_domain) + users_path
        if ' boundary=' in self.headers['Content-type']:
            boundary = self.headers['Content-type'].split('boundary=')[1]
            if ';' in boundary:
                boundary = boundary.split(';')[0]

            # get the nickname
            nickname = get_nickname_from_actor(actor_str)
            if not nickname:
                print('WARN: nickname not found in ' + actor_str)
                self._redirect_headers(actor_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            length = int(self.headers['Content-length'])

            # check that the POST isn't too large
            if length > self.server.max_post_length:
                print('Maximum profile data length exceeded ' +
                      str(length))
                self._redirect_headers(actor_str, cookie, calling_domain)
                self.server.postreq_busy = False
                return

            try:
                # read the bytes of the http form POST
                post_bytes = self.rfile.read(length)
            except SocketError as ex:
                if ex.errno == errno.ECONNRESET:
                    print('EX: connection was reset while ' +
                          'reading bytes from http form POST')
                else:
                    print('EX: error while reading bytes ' +
                          'from http form POST')
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return
            except ValueError as ex:
                print('EX: failed to read bytes for POST, ' + str(ex))
                self.send_response(400)
                self.end_headers()
                self.server.postreq_busy = False
                return

            admin_nickname = get_config_param(self.server.base_dir, 'admin')

            # get the various avatar, banner and background images
            actor_changed = True
            profile_media_types = (
                'avatar', 'image',
                'banner', 'search_banner',
                'instanceLogo',
                'left_col_image', 'right_col_image',
                'submitImportTheme'
            )
            profile_media_types_uploaded = {}
            for m_type in profile_media_types:
                # some images can only be changed by the admin
                if m_type == 'instanceLogo':
                    if nickname != admin_nickname:
                        print('WARN: only the admin can change ' +
                              'instance logo')
                        continue

                if debug:
                    print('DEBUG: profile update extracting ' + m_type +
                          ' image, zip or font from POST')
                media_bytes, post_bytes = \
                    extract_media_in_form_post(post_bytes, boundary, m_type)
                if media_bytes:
                    if debug:
                        print('DEBUG: profile update ' + m_type +
                              ' image, zip or font was found. ' +
                              str(len(media_bytes)) + ' bytes')
                else:
                    if debug:
                        print('DEBUG: profile update, no ' + m_type +
                              ' image, zip or font was found in POST')
                    continue

                # Note: a .temp extension is used here so that at no
                # time is an image with metadata publicly exposed,
                # even for a few mS
                if m_type == 'instanceLogo':
                    filename_base = \
                        base_dir + '/accounts/login.temp'
                elif m_type == 'submitImportTheme':
                    if not os.path.isdir(base_dir + '/imports'):
                        os.mkdir(base_dir + '/imports')
                    filename_base = \
                        base_dir + '/imports/newtheme.zip'
                    if os.path.isfile(filename_base):
                        try:
                            os.remove(filename_base)
                        except OSError:
                            print('EX: _profile_edit unable to delete ' +
                                  filename_base)
                else:
                    filename_base = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/' + m_type + '.temp'

                filename, attachment_media_type = \
                    save_media_in_form_post(media_bytes, debug,
                                            filename_base)
                if filename:
                    print('Profile update POST ' + m_type +
                          ' media, zip or font filename is ' + filename)
                else:
                    print('Profile update, no ' + m_type +
                          ' media, zip or font filename in POST')
                    continue

                if m_type == 'submitImportTheme':
                    if nickname == admin_nickname or \
                       is_artist(base_dir, nickname):
                        if import_theme(base_dir, filename):
                            print(nickname + ' uploaded a theme')
                    else:
                        print('Only admin or artist can import a theme')
                    continue

                post_image_filename = filename.replace('.temp', '')
                if debug:
                    print('DEBUG: POST ' + m_type +
                          ' media removing metadata')
                # remove existing etag
                if os.path.isfile(post_image_filename + '.etag'):
                    try:
                        os.remove(post_image_filename + '.etag')
                    except OSError:
                        print('EX: _profile_edit unable to delete ' +
                              post_image_filename + '.etag')

                city = get_spoofed_city(self.server.city,
                                        base_dir, nickname, domain)

                if self.server.low_bandwidth:
                    convert_image_to_low_bandwidth(filename)
                process_meta_data(base_dir, nickname, domain,
                                  filename, post_image_filename, city,
                                  content_license_url)
                if os.path.isfile(post_image_filename):
                    print('profile update POST ' + m_type +
                          ' image, zip or font saved to ' +
                          post_image_filename)
                    if m_type != 'instanceLogo':
                        last_part_of_image_filename = \
                            post_image_filename.split('/')[-1]
                        profile_media_types_uploaded[m_type] = \
                            last_part_of_image_filename
                        actor_changed = True
                else:
                    print('ERROR: profile update POST ' + m_type +
                          ' image or font could not be saved to ' +
                          post_image_filename)

            post_bytes_str = post_bytes.decode('utf-8')
            redirect_path = ''
            check_name_and_bio = False
            on_final_welcome_screen = False
            if 'name="previewAvatar"' in post_bytes_str:
                redirect_path = '/welcome_profile'
            elif 'name="initialWelcomeScreen"' in post_bytes_str:
                redirect_path = '/welcome'
            elif 'name="finalWelcomeScreen"' in post_bytes_str:
                check_name_and_bio = True
                redirect_path = '/welcome_final'
            elif 'name="welcomeCompleteButton"' in post_bytes_str:
                redirect_path = '/' + self.server.default_timeline
                welcome_screen_is_complete(self.server.base_dir, nickname,
                                           self.server.domain)
                on_final_welcome_screen = True
            elif 'name="submitExportTheme"' in post_bytes_str:
                print('submitExportTheme')
                theme_download_path = actor_str
                if export_theme(self.server.base_dir,
                                self.server.theme_name):
                    theme_download_path += \
                        '/exports/' + self.server.theme_name + '.zip'
                print('submitExportTheme path=' + theme_download_path)
                self._redirect_headers(theme_download_path,
                                       cookie, calling_domain)
                self.server.postreq_busy = False
                return

            # extract all of the text fields into a dict
            fields = \
                extract_text_fields_in_post(post_bytes, boundary, debug)
            if debug:
                if fields:
                    print('DEBUG: profile update text ' +
                          'field extracted from POST ' + str(fields))
                else:
                    print('WARN: profile update, no text ' +
                          'fields could be extracted from POST')

            # load the json for the actor for this user
            actor_filename = \
                acct_dir(base_dir, nickname, domain) + '.json'
            if os.path.isfile(actor_filename):
                actor_json = load_json(actor_filename)
                if actor_json:
                    if not actor_json.get('discoverable'):
                        # discoverable in profile directory
                        # which isn't implemented in Epicyon
                        actor_json['discoverable'] = True
                        actor_changed = True
                    if actor_json.get('capabilityAcquisitionEndpoint'):
                        del actor_json['capabilityAcquisitionEndpoint']
                        actor_changed = True
                    # update the avatar/image url file extension
                    uploads = profile_media_types_uploaded.items()
                    for m_type, last_part in uploads:
                        rep_str = '/' + last_part
                        if m_type == 'avatar':
                            actor_url = actor_json['icon']['url']
                            last_part_of_url = actor_url.split('/')[-1]
                            srch_str = '/' + last_part_of_url
                            actor_url = actor_url.replace(srch_str, rep_str)
                            actor_json['icon']['url'] = actor_url
                            print('actor_url: ' + actor_url)
                            if '.' in actor_url:
                                img_ext = actor_url.split('.')[-1]
                                if img_ext == 'jpg':
                                    img_ext = 'jpeg'
                                actor_json['icon']['mediaType'] = \
                                    'image/' + img_ext
                        elif m_type == 'image':
                            last_part_of_url = \
                                actor_json['image']['url'].split('/')[-1]
                            srch_str = '/' + last_part_of_url
                            actor_json['image']['url'] = \
                                actor_json['image']['url'].replace(srch_str,
                                                                   rep_str)
                            if '.' in actor_json['image']['url']:
                                img_ext = \
                                    actor_json['image']['url'].split('.')[-1]
                                if img_ext == 'jpg':
                                    img_ext = 'jpeg'
                                actor_json['image']['mediaType'] = \
                                    'image/' + img_ext

                    # set skill levels
                    skill_ctr = 1
                    actor_skills_ctr = no_of_actor_skills(actor_json)
                    while skill_ctr < 10:
                        skill_name = \
                            fields.get('skillName' + str(skill_ctr))
                        if not skill_name:
                            skill_ctr += 1
                            continue
                        if is_filtered(base_dir, nickname, domain, skill_name):
                            skill_ctr += 1
                            continue
                        skill_value = \
                            fields.get('skillValue' + str(skill_ctr))
                        if not skill_value:
                            skill_ctr += 1
                            continue
                        if not actor_has_skill(actor_json, skill_name):
                            actor_changed = True
                        else:
                            if actor_skill_value(actor_json, skill_name) != \
                               int(skill_value):
                                actor_changed = True
                        set_actor_skill_level(actor_json,
                                              skill_name, int(skill_value))
                        skills_str = self.server.translate['Skills']
                        skills_str = skills_str.lower()
                        set_hashtag_category(base_dir, skill_name,
                                             skills_str, False)
                        skill_ctr += 1
                    if no_of_actor_skills(actor_json) != \
                       actor_skills_ctr:
                        actor_changed = True

                    # change password
                    if fields.get('password') and \
                       fields.get('passwordconfirm'):
                        fields['password'] = \
                            remove_line_endings(fields['password'])
                        fields['passwordconfirm'] = \
                            remove_line_endings(fields['passwordconfirm'])
                        if valid_password(fields['password']) and \
                           fields['password'] == fields['passwordconfirm']:
                            # set password
                            store_basic_credentials(base_dir, nickname,
                                                    fields['password'])

                    # reply interval in hours
                    if fields.get('replyhours'):
                        if fields['replyhours'].isdigit():
                            set_reply_interval_hours(base_dir,
                                                     nickname, domain,
                                                     fields['replyhours'])

                    # change city
                    if fields.get('cityDropdown'):
                        city_filename = \
                            acct_dir(base_dir, nickname, domain) + '/city.txt'
                        try:
                            with open(city_filename, 'w+') as fp_city:
                                fp_city.write(fields['cityDropdown'])
                        except OSError:
                            print('EX: unable to write city ' + city_filename)

                    # change displayed name
                    if fields.get('displayNickname'):
                        if fields['displayNickname'] != actor_json['name']:
                            display_name = \
                                remove_html(fields['displayNickname'])
                            if not is_filtered(base_dir,
                                               nickname, domain,
                                               display_name):
                                actor_json['name'] = display_name
                            else:
                                actor_json['name'] = nickname
                                if check_name_and_bio:
                                    redirect_path = 'previewAvatar'
                            actor_changed = True
                    else:
                        if check_name_and_bio:
                            redirect_path = 'previewAvatar'

                    if nickname == admin_nickname or \
                       is_artist(base_dir, nickname):
                        # change theme
                        if fields.get('themeDropdown'):
                            self.server.theme_name = fields['themeDropdown']
                            set_theme(base_dir, self.server.theme_name, domain,
                                      allow_local_network_access,
                                      system_language,
                                      self.server.dyslexic_font)
                            self.server.text_mode_banner = \
                                get_text_mode_banner(self.server.base_dir)
                            self.server.iconsCache = {}
                            self.server.fontsCache = {}
                            self.server.show_publish_as_icon = \
                                get_config_param(self.server.base_dir,
                                                 'showPublishAsIcon')
                            self.server.full_width_tl_button_header = \
                                get_config_param(self.server.base_dir,
                                                 'fullWidthTlButtonHeader')
                            self.server.icons_as_buttons = \
                                get_config_param(self.server.base_dir,
                                                 'iconsAsButtons')
                            self.server.rss_icon_at_top = \
                                get_config_param(self.server.base_dir,
                                                 'rssIconAtTop')
                            self.server.publish_button_at_top = \
                                get_config_param(self.server.base_dir,
                                                 'publishButtonAtTop')
                            set_news_avatar(base_dir,
                                            fields['themeDropdown'],
                                            http_prefix,
                                            domain,
                                            domain_full)

                    if nickname == admin_nickname:
                        # change media instance status
                        if fields.get('mediaInstance'):
                            self.server.media_instance = False
                            self.server.default_timeline = 'inbox'
                            if fields['mediaInstance'] == 'on':
                                self.server.media_instance = True
                                self.server.blogs_instance = False
                                self.server.news_instance = False
                                self.server.default_timeline = 'tlmedia'
                            set_config_param(base_dir, "mediaInstance",
                                             self.server.media_instance)
                            set_config_param(base_dir, "blogsInstance",
                                             self.server.blogs_instance)
                            set_config_param(base_dir, "newsInstance",
                                             self.server.news_instance)
                        else:
                            if self.server.media_instance:
                                self.server.media_instance = False
                                self.server.default_timeline = 'inbox'
                                set_config_param(base_dir, "mediaInstance",
                                                 self.server.media_instance)

                        # is this a news theme?
                        if is_news_theme_name(self.server.base_dir,
                                              self.server.theme_name):
                            fields['newsInstance'] = 'on'

                        # change news instance status
                        if fields.get('newsInstance'):
                            self.server.news_instance = False
                            self.server.default_timeline = 'inbox'
                            if fields['newsInstance'] == 'on':
                                self.server.news_instance = True
                                self.server.blogs_instance = False
                                self.server.media_instance = False
                                self.server.default_timeline = 'tlfeatures'
                            set_config_param(base_dir, "mediaInstance",
                                             self.server.media_instance)
                            set_config_param(base_dir, "blogsInstance",
                                             self.server.blogs_instance)
                            set_config_param(base_dir, "newsInstance",
                                             self.server.news_instance)
                        else:
                            if self.server.news_instance:
                                self.server.news_instance = False
                                self.server.default_timeline = 'inbox'
                                set_config_param(base_dir, "newsInstance",
                                                 self.server.media_instance)

                        # change blog instance status
                        if fields.get('blogsInstance'):
                            self.server.blogs_instance = False
                            self.server.default_timeline = 'inbox'
                            if fields['blogsInstance'] == 'on':
                                self.server.blogs_instance = True
                                self.server.media_instance = False
                                self.server.news_instance = False
                                self.server.default_timeline = 'tlblogs'
                            set_config_param(base_dir, "blogsInstance",
                                             self.server.blogs_instance)
                            set_config_param(base_dir, "mediaInstance",
                                             self.server.media_instance)
                            set_config_param(base_dir, "newsInstance",
                                             self.server.news_instance)
                        else:
                            if self.server.blogs_instance:
                                self.server.blogs_instance = False
                                self.server.default_timeline = 'inbox'
                                set_config_param(base_dir, "blogsInstance",
                                                 self.server.blogs_instance)

                        # change instance title
                        if fields.get('instanceTitle'):
                            curr_instance_title = \
                                get_config_param(base_dir, 'instanceTitle')
                            if fields['instanceTitle'] != curr_instance_title:
                                set_config_param(base_dir, 'instanceTitle',
                                                 fields['instanceTitle'])

                        # change YouTube alternate domain
                        if fields.get('ytdomain'):
                            curr_yt_domain = self.server.yt_replace_domain
                            if fields['ytdomain'] != curr_yt_domain:
                                new_yt_domain = fields['ytdomain']
                                if '://' in new_yt_domain:
                                    new_yt_domain = \
                                        new_yt_domain.split('://')[1]
                                if '/' in new_yt_domain:
                                    new_yt_domain = new_yt_domain.split('/')[0]
                                if '.' in new_yt_domain:
                                    set_config_param(base_dir, 'youtubedomain',
                                                     new_yt_domain)
                                    self.server.yt_replace_domain = \
                                        new_yt_domain
                        else:
                            set_config_param(base_dir, 'youtubedomain', '')
                            self.server.yt_replace_domain = None

                        # change twitter alternate domain
                        if fields.get('twitterdomain'):
                            curr_twitter_domain = \
                                self.server.twitter_replacement_domain
                            if fields['twitterdomain'] != curr_twitter_domain:
                                new_twitter_domain = fields['twitterdomain']
                                if '://' in new_twitter_domain:
                                    new_twitter_domain = \
                                        new_twitter_domain.split('://')[1]
                                if '/' in new_twitter_domain:
                                    new_twitter_domain = \
                                        new_twitter_domain.split('/')[0]
                                if '.' in new_twitter_domain:
                                    set_config_param(base_dir, 'twitterdomain',
                                                     new_twitter_domain)
                                    self.server.twitter_replacement_domain = \
                                        new_twitter_domain
                        else:
                            set_config_param(base_dir, 'twitterdomain', '')
                            self.server.twitter_replacement_domain = None

                        # change custom post submit button text
                        curr_custom_submit_text = \
                            get_config_param(base_dir, 'customSubmitText')
                        if fields.get('customSubmitText'):
                            if fields['customSubmitText'] != \
                               curr_custom_submit_text:
                                customText = fields['customSubmitText']
                                set_config_param(base_dir, 'customSubmitText',
                                                 customText)
                        else:
                            if curr_custom_submit_text:
                                set_config_param(base_dir, 'customSubmitText',
                                                 '')

                        # libretranslate URL
                        curr_libretranslate_url = \
                            get_config_param(base_dir,
                                             'libretranslateUrl')
                        if fields.get('libretranslateUrl'):
                            if fields['libretranslateUrl'] != \
                               curr_libretranslate_url:
                                lt_url = fields['libretranslateUrl']
                                if '://' in lt_url and \
                                   '.' in lt_url:
                                    set_config_param(base_dir,
                                                     'libretranslateUrl',
                                                     lt_url)
                        else:
                            if curr_libretranslate_url:
                                set_config_param(base_dir,
                                                 'libretranslateUrl', '')

                        # libretranslate API Key
                        curr_libretranslate_api_key = \
                            get_config_param(base_dir,
                                             'libretranslateApiKey')
                        if fields.get('libretranslateApiKey'):
                            if fields['libretranslateApiKey'] != \
                               curr_libretranslate_api_key:
                                lt_api_key = fields['libretranslateApiKey']
                                set_config_param(base_dir,
                                                 'libretranslateApiKey',
                                                 lt_api_key)
                        else:
                            if curr_libretranslate_api_key:
                                set_config_param(base_dir,
                                                 'libretranslateApiKey', '')

                        # change instance short description
                        if fields.get('contentLicenseUrl'):
                            if fields['contentLicenseUrl'] != \
                               self.server.content_license_url:
                                license_str = fields['contentLicenseUrl']
                                set_config_param(base_dir,
                                                 'contentLicenseUrl',
                                                 license_str)
                                self.server.content_license_url = \
                                    license_str
                        else:
                            license_str = \
                                'https://creativecommons.org/licenses/by/4.0'
                            set_config_param(base_dir,
                                             'contentLicenseUrl',
                                             license_str)
                            self.server.content_license_url = license_str

                        # change instance short description
                        curr_instance_description_short = \
                            get_config_param(base_dir,
                                             'instanceDescriptionShort')
                        if fields.get('instanceDescriptionShort'):
                            if fields['instanceDescriptionShort'] != \
                               curr_instance_description_short:
                                idesc = fields['instanceDescriptionShort']
                                set_config_param(base_dir,
                                                 'instanceDescriptionShort',
                                                 idesc)
                        else:
                            if curr_instance_description_short:
                                set_config_param(base_dir,
                                                 'instanceDescriptionShort',
                                                 '')

                        # change instance description
                        curr_instance_description = \
                            get_config_param(base_dir, 'instanceDescription')
                        if fields.get('instanceDescription'):
                            if fields['instanceDescription'] != \
                               curr_instance_description:
                                set_config_param(base_dir,
                                                 'instanceDescription',
                                                 fields['instanceDescription'])
                        else:
                            if curr_instance_description:
                                set_config_param(base_dir,
                                                 'instanceDescription', '')

                    # change email address
                    current_email_address = get_email_address(actor_json)
                    if fields.get('email'):
                        if fields['email'] != current_email_address:
                            set_email_address(actor_json, fields['email'])
                            actor_changed = True
                    else:
                        if current_email_address:
                            set_email_address(actor_json, '')
                            actor_changed = True

                    # change xmpp address
                    current_xmpp_address = get_xmpp_address(actor_json)
                    if fields.get('xmppAddress'):
                        if fields['xmppAddress'] != current_xmpp_address:
                            set_xmpp_address(actor_json,
                                             fields['xmppAddress'])
                            actor_changed = True
                    else:
                        if current_xmpp_address:
                            set_xmpp_address(actor_json, '')
                            actor_changed = True

                    # change matrix address
                    current_matrix_address = get_matrix_address(actor_json)
                    if fields.get('matrixAddress'):
                        if fields['matrixAddress'] != current_matrix_address:
                            set_matrix_address(actor_json,
                                               fields['matrixAddress'])
                            actor_changed = True
                    else:
                        if current_matrix_address:
                            set_matrix_address(actor_json, '')
                            actor_changed = True

                    # change SSB address
                    current_ssb_address = get_ssb_address(actor_json)
                    if fields.get('ssbAddress'):
                        if fields['ssbAddress'] != current_ssb_address:
                            set_ssb_address(actor_json,
                                            fields['ssbAddress'])
                            actor_changed = True
                    else:
                        if current_ssb_address:
                            set_ssb_address(actor_json, '')
                            actor_changed = True

                    # change blog address
                    current_blog_address = get_blog_address(actor_json)
                    if fields.get('blogAddress'):
                        if fields['blogAddress'] != current_blog_address:
                            set_blog_address(actor_json,
                                             fields['blogAddress'])
                            actor_changed = True
                    else:
                        if current_blog_address:
                            set_blog_address(actor_json, '')
                            actor_changed = True

                    # change Languages address
                    current_show_languages = get_actor_languages(actor_json)
                    if fields.get('showLanguages'):
                        if fields['showLanguages'] != current_show_languages:
                            set_actor_languages(base_dir, actor_json,
                                                fields['showLanguages'])
                            actor_changed = True
                    else:
                        if current_show_languages:
                            set_actor_languages(base_dir, actor_json, '')
                            actor_changed = True

                    # change tox address
                    current_tox_address = get_tox_address(actor_json)
                    if fields.get('toxAddress'):
                        if fields['toxAddress'] != current_tox_address:
                            set_tox_address(actor_json,
                                            fields['toxAddress'])
                            actor_changed = True
                    else:
                        if current_tox_address:
                            set_tox_address(actor_json, '')
                            actor_changed = True

                    # change briar address
                    current_briar_address = get_briar_address(actor_json)
                    if fields.get('briarAddress'):
                        if fields['briarAddress'] != current_briar_address:
                            set_briar_address(actor_json,
                                              fields['briarAddress'])
                            actor_changed = True
                    else:
                        if current_briar_address:
                            set_briar_address(actor_json, '')
                            actor_changed = True

                    # change jami address
                    current_jami_address = get_jami_address(actor_json)
                    if fields.get('jamiAddress'):
                        if fields['jamiAddress'] != current_jami_address:
                            set_jami_address(actor_json,
                                             fields['jamiAddress'])
                            actor_changed = True
                    else:
                        if current_jami_address:
                            set_jami_address(actor_json, '')
                            actor_changed = True

                    # change cwtch address
                    current_cwtch_address = get_cwtch_address(actor_json)
                    if fields.get('cwtchAddress'):
                        if fields['cwtchAddress'] != current_cwtch_address:
                            set_cwtch_address(actor_json,
                                              fields['cwtchAddress'])
                            actor_changed = True
                    else:
                        if current_cwtch_address:
                            set_cwtch_address(actor_json, '')
                            actor_changed = True

                    # change Enigma public key
                    currentenigma_pub_key = get_enigma_pub_key(actor_json)
                    if fields.get('enigmapubkey'):
                        if fields['enigmapubkey'] != currentenigma_pub_key:
                            set_enigma_pub_key(actor_json,
                                               fields['enigmapubkey'])
                            actor_changed = True
                    else:
                        if currentenigma_pub_key:
                            set_enigma_pub_key(actor_json, '')
                            actor_changed = True

                    # change PGP public key
                    currentpgp_pub_key = get_pgp_pub_key(actor_json)
                    if fields.get('pgp'):
                        if fields['pgp'] != currentpgp_pub_key:
                            set_pgp_pub_key(actor_json,
                                            fields['pgp'])
                            actor_changed = True
                    else:
                        if currentpgp_pub_key:
                            set_pgp_pub_key(actor_json, '')
                            actor_changed = True

                    # change PGP fingerprint
                    currentpgp_fingerprint = get_pgp_fingerprint(actor_json)
                    if fields.get('openpgp'):
                        if fields['openpgp'] != currentpgp_fingerprint:
                            set_pgp_fingerprint(actor_json,
                                                fields['openpgp'])
                            actor_changed = True
                    else:
                        if currentpgp_fingerprint:
                            set_pgp_fingerprint(actor_json, '')
                            actor_changed = True

                    # change donation link
                    current_donate_url = get_donation_url(actor_json)
                    if fields.get('donateUrl'):
                        if fields['donateUrl'] != current_donate_url:
                            set_donation_url(actor_json,
                                             fields['donateUrl'])
                            actor_changed = True
                    else:
                        if current_donate_url:
                            set_donation_url(actor_json, '')
                            actor_changed = True

                    # change website
                    current_website = \
                        get_website(actor_json, self.server.translate)
                    if fields.get('websiteUrl'):
                        if fields['websiteUrl'] != current_website:
                            set_website(actor_json,
                                        fields['websiteUrl'],
                                        self.server.translate)
                            actor_changed = True
                    else:
                        if current_website:
                            set_website(actor_json, '', self.server.translate)
                            actor_changed = True

                    # account moved to new address
                    moved_to = ''
                    if actor_json.get('movedTo'):
                        moved_to = actor_json['movedTo']
                    if fields.get('movedTo'):
                        if fields['movedTo'] != moved_to and \
                           '://' in fields['movedTo'] and \
                           '.' in fields['movedTo']:
                            actor_json['movedTo'] = moved_to
                            actor_changed = True
                    else:
                        if moved_to:
                            del actor_json['movedTo']
                            actor_changed = True

                    # Other accounts (alsoKnownAs)
                    occupation_name = get_occupation_name(actor_json)
                    if fields.get('occupationName'):
                        fields['occupationName'] = \
                            remove_html(fields['occupationName'])
                        if occupation_name != \
                           fields['occupationName']:
                            set_occupation_name(actor_json,
                                                fields['occupationName'])
                            actor_changed = True
                    else:
                        if occupation_name:
                            set_occupation_name(actor_json, '')
                            actor_changed = True

                    # Other accounts (alsoKnownAs)
                    also_known_as = []
                    if actor_json.get('alsoKnownAs'):
                        also_known_as = actor_json['alsoKnownAs']
                    if fields.get('alsoKnownAs'):
                        also_known_as_str = ''
                        also_known_as_ctr = 0
                        for alt_actor in also_known_as:
                            if also_known_as_ctr > 0:
                                also_known_as_str += ', '
                            also_known_as_str += alt_actor
                            also_known_as_ctr += 1
                        if fields['alsoKnownAs'] != also_known_as_str and \
                           '://' in fields['alsoKnownAs'] and \
                           '@' not in fields['alsoKnownAs'] and \
                           '.' in fields['alsoKnownAs']:
                            if ';' in fields['alsoKnownAs']:
                                fields['alsoKnownAs'] = \
                                    fields['alsoKnownAs'].replace(';', ',')
                            new_also_known_as = \
                                fields['alsoKnownAs'].split(',')
                            also_known_as = []
                            for alt_actor in new_also_known_as:
                                alt_actor = alt_actor.strip()
                                if '://' in alt_actor and '.' in alt_actor:
                                    if alt_actor not in also_known_as:
                                        also_known_as.append(alt_actor)
                            actor_json['alsoKnownAs'] = also_known_as
                            actor_changed = True
                    else:
                        if also_known_as:
                            del actor_json['alsoKnownAs']
                            actor_changed = True

                    # change user bio
                    if fields.get('bio'):
                        if fields['bio'] != actor_json['summary']:
                            bio_str = remove_html(fields['bio'])
                            if not is_filtered(base_dir,
                                               nickname, domain, bio_str):
                                actor_tags = {}
                                actor_json['summary'] = \
                                    add_html_tags(base_dir,
                                                  http_prefix,
                                                  nickname,
                                                  domain_full,
                                                  bio_str, [], actor_tags)
                                if actor_tags:
                                    actor_json['tag'] = []
                                    for _, tag in actor_tags.items():
                                        actor_json['tag'].append(tag)
                                actor_changed = True
                            else:
                                if check_name_and_bio:
                                    redirect_path = 'previewAvatar'
                    else:
                        if check_name_and_bio:
                            redirect_path = 'previewAvatar'

                    admin_nickname = \
                        get_config_param(base_dir, 'admin')

                    if admin_nickname:
                        # whether to require jsonld signatures
                        # on all incoming posts
                        if path.startswith('/users/' +
                                           admin_nickname + '/'):
                            show_node_info_accounts = False
                            if fields.get('showNodeInfoAccounts'):
                                if fields['showNodeInfoAccounts'] == 'on':
                                    show_node_info_accounts = True
                            self.server.show_node_info_accounts = \
                                show_node_info_accounts
                            set_config_param(base_dir,
                                             "showNodeInfoAccounts",
                                             show_node_info_accounts)

                            show_node_info_version = False
                            if fields.get('showNodeInfoVersion'):
                                if fields['showNodeInfoVersion'] == 'on':
                                    show_node_info_version = True
                            self.server.show_node_info_version = \
                                show_node_info_version
                            set_config_param(base_dir,
                                             "showNodeInfoVersion",
                                             show_node_info_version)

                            verify_all_signatures = False
                            if fields.get('verifyallsignatures'):
                                if fields['verifyallsignatures'] == 'on':
                                    verify_all_signatures = True
                            self.server.verify_all_signatures = \
                                verify_all_signatures
                            set_config_param(base_dir, "verifyAllSignatures",
                                             verify_all_signatures)

                            broch_mode = False
                            if fields.get('brochMode'):
                                if fields['brochMode'] == 'on':
                                    broch_mode = True
                            curr_broch_mode = \
                                get_config_param(base_dir, "brochMode")
                            if broch_mode != curr_broch_mode:
                                set_broch_mode(self.server.base_dir,
                                               self.server.domain_full,
                                               broch_mode)
                                set_config_param(base_dir, 'brochMode',
                                                 broch_mode)

                            # shared item federation domains
                            si_domain_updated = False
                            fed_domains_variable = \
                                "sharedItemsFederatedDomains"
                            fed_domains_str = \
                                get_config_param(base_dir,
                                                 fed_domains_variable)
                            if not fed_domains_str:
                                fed_domains_str = ''
                            shared_items_form_str = ''
                            if fields.get('shareDomainList'):
                                shared_it_list = \
                                    fed_domains_str.split(',')
                                for shared_federated_domain in shared_it_list:
                                    shared_items_form_str += \
                                        shared_federated_domain.strip() + '\n'

                                share_domain_list = fields['shareDomainList']
                                if share_domain_list != \
                                   shared_items_form_str:
                                    shared_items_form_str2 = \
                                        share_domain_list.replace('\n', ',')
                                    shared_items_field = \
                                        "sharedItemsFederatedDomains"
                                    set_config_param(base_dir,
                                                     shared_items_field,
                                                     shared_items_form_str2)
                                    si_domain_updated = True
                            else:
                                if fed_domains_str:
                                    shared_items_field = \
                                        "sharedItemsFederatedDomains"
                                    set_config_param(base_dir,
                                                     shared_items_field,
                                                     '')
                                    si_domain_updated = True
                            if si_domain_updated:
                                si_domains = shared_items_form_str.split('\n')
                                si_tokens = \
                                    self.server.shared_item_federation_tokens
                                self.server.shared_items_federated_domains = \
                                    si_domains
                                domain_full = self.server.domain_full
                                base_dir = \
                                    self.server.base_dir
                                self.server.shared_item_federation_tokens = \
                                    merge_shared_item_tokens(base_dir,
                                                             domain_full,
                                                             si_domains,
                                                             si_tokens)

                        # change moderators list
                        if fields.get('moderators'):
                            if path.startswith('/users/' +
                                               admin_nickname + '/'):
                                moderators_file = \
                                    base_dir + \
                                    '/accounts/moderators.txt'
                                clear_moderator_status(base_dir)
                                if ',' in fields['moderators']:
                                    # if the list was given as comma separated
                                    mods = fields['moderators'].split(',')
                                    try:
                                        with open(moderators_file,
                                                  'w+') as modfile:
                                            for mod_nick in mods:
                                                mod_nick = mod_nick.strip()
                                                mod_dir = base_dir + \
                                                    '/accounts/' + mod_nick + \
                                                    '@' + domain
                                                if os.path.isdir(mod_dir):
                                                    modfile.write(mod_nick +
                                                                  '\n')
                                    except OSError:
                                        print('EX: ' +
                                              'unable to write moderators ' +
                                              moderators_file)

                                    for mod_nick in mods:
                                        mod_nick = mod_nick.strip()
                                        mod_dir = base_dir + \
                                            '/accounts/' + mod_nick + \
                                            '@' + domain
                                        if os.path.isdir(mod_dir):
                                            set_role(base_dir,
                                                     mod_nick, domain,
                                                     'moderator')
                                else:
                                    # nicknames on separate lines
                                    mods = fields['moderators'].split('\n')
                                    try:
                                        with open(moderators_file,
                                                  'w+') as modfile:
                                            for mod_nick in mods:
                                                mod_nick = mod_nick.strip()
                                                mod_dir = \
                                                    base_dir + \
                                                    '/accounts/' + mod_nick + \
                                                    '@' + domain
                                                if os.path.isdir(mod_dir):
                                                    modfile.write(mod_nick +
                                                                  '\n')
                                    except OSError:
                                        print('EX: ' +
                                              'unable to write moderators 2 ' +
                                              moderators_file)

                                    for mod_nick in mods:
                                        mod_nick = mod_nick.strip()
                                        mod_dir = \
                                            base_dir + \
                                            '/accounts/' + \
                                            mod_nick + '@' + \
                                            domain
                                        if os.path.isdir(mod_dir):
                                            set_role(base_dir,
                                                     mod_nick, domain,
                                                     'moderator')

                        # change site editors list
                        if fields.get('editors'):
                            if path.startswith('/users/' +
                                               admin_nickname + '/'):
                                editors_file = \
                                    base_dir + \
                                    '/accounts/editors.txt'
                                clear_editor_status(base_dir)
                                if ',' in fields['editors']:
                                    # if the list was given as comma separated
                                    eds = fields['editors'].split(',')
                                    try:
                                        with open(editors_file, 'w+') as edfil:
                                            for ed_nick in eds:
                                                ed_nick = ed_nick.strip()
                                                ed_dir = base_dir + \
                                                    '/accounts/' + ed_nick + \
                                                    '@' + domain
                                                if os.path.isdir(ed_dir):
                                                    edfil.write(ed_nick + '\n')
                                    except OSError as ex:
                                        print('EX: unable to write editors ' +
                                              editors_file + ' ' + str(ex))

                                    for ed_nick in eds:
                                        ed_nick = ed_nick.strip()
                                        ed_dir = base_dir + \
                                            '/accounts/' + ed_nick + \
                                            '@' + domain
                                        if os.path.isdir(ed_dir):
                                            set_role(base_dir,
                                                     ed_nick, domain,
                                                     'editor')
                                else:
                                    # nicknames on separate lines
                                    eds = fields['editors'].split('\n')
                                    try:
                                        with open(editors_file,
                                                  'w+') as edfile:
                                            for ed_nick in eds:
                                                ed_nick = ed_nick.strip()
                                                ed_dir = \
                                                    base_dir + \
                                                    '/accounts/' + ed_nick + \
                                                    '@' + domain
                                                if os.path.isdir(ed_dir):
                                                    edfile.write(ed_nick +
                                                                 '\n')
                                    except OSError as ex:
                                        print('EX: unable to write editors ' +
                                              editors_file + ' ' + str(ex))

                                    for ed_nick in eds:
                                        ed_nick = ed_nick.strip()
                                        ed_dir = \
                                            base_dir + \
                                            '/accounts/' + \
                                            ed_nick + '@' + \
                                            domain
                                        if os.path.isdir(ed_dir):
                                            set_role(base_dir,
                                                     ed_nick, domain,
                                                     'editor')

                        # change site counselors list
                        if fields.get('counselors'):
                            if path.startswith('/users/' +
                                               admin_nickname + '/'):
                                counselors_file = \
                                    base_dir + \
                                    '/accounts/counselors.txt'
                                clear_counselor_status(base_dir)
                                if ',' in fields['counselors']:
                                    # if the list was given as comma separated
                                    eds = fields['counselors'].split(',')
                                    try:
                                        with open(counselors_file,
                                                  'w+') as edfile:
                                            for ed_nick in eds:
                                                ed_nick = ed_nick.strip()
                                                ed_dir = base_dir + \
                                                    '/accounts/' + ed_nick + \
                                                    '@' + domain
                                                if os.path.isdir(ed_dir):
                                                    edfile.write(ed_nick +
                                                                 '\n')
                                    except OSError as ex:
                                        print('EX: ' +
                                              'unable to write counselors ' +
                                              counselors_file + ' ' + str(ex))

                                    for ed_nick in eds:
                                        ed_nick = ed_nick.strip()
                                        ed_dir = base_dir + \
                                            '/accounts/' + ed_nick + \
                                            '@' + domain
                                        if os.path.isdir(ed_dir):
                                            set_role(base_dir,
                                                     ed_nick, domain,
                                                     'counselor')
                                else:
                                    # nicknames on separate lines
                                    eds = fields['counselors'].split('\n')
                                    try:
                                        with open(counselors_file,
                                                  'w+') as edfile:
                                            for ed_nick in eds:
                                                ed_nick = ed_nick.strip()
                                                ed_dir = \
                                                    base_dir + \
                                                    '/accounts/' + ed_nick + \
                                                    '@' + domain
                                                if os.path.isdir(ed_dir):
                                                    edfile.write(ed_nick +
                                                                 '\n')
                                    except OSError as ex:
                                        print('EX: ' +
                                              'unable to write counselors ' +
                                              counselors_file + ' ' + str(ex))

                                    for ed_nick in eds:
                                        ed_nick = ed_nick.strip()
                                        ed_dir = \
                                            base_dir + \
                                            '/accounts/' + \
                                            ed_nick + '@' + \
                                            domain
                                        if os.path.isdir(ed_dir):
                                            set_role(base_dir,
                                                     ed_nick, domain,
                                                     'counselor')

                        # change site artists list
                        if fields.get('artists'):
                            if path.startswith('/users/' +
                                               admin_nickname + '/'):
                                artists_file = \
                                    base_dir + \
                                    '/accounts/artists.txt'
                                clear_artist_status(base_dir)
                                if ',' in fields['artists']:
                                    # if the list was given as comma separated
                                    eds = fields['artists'].split(',')
                                    try:
                                        with open(artists_file, 'w+') as edfil:
                                            for ed_nick in eds:
                                                ed_nick = ed_nick.strip()
                                                ed_dir = base_dir + \
                                                    '/accounts/' + ed_nick + \
                                                    '@' + domain
                                                if os.path.isdir(ed_dir):
                                                    edfil.write(ed_nick + '\n')
                                    except OSError as ex:
                                        print('EX: unable to write artists ' +
                                              artists_file + ' ' + str(ex))

                                    for ed_nick in eds:
                                        ed_nick = ed_nick.strip()
                                        ed_dir = base_dir + \
                                            '/accounts/' + ed_nick + \
                                            '@' + domain
                                        if os.path.isdir(ed_dir):
                                            set_role(base_dir,
                                                     ed_nick, domain,
                                                     'artist')
                                else:
                                    # nicknames on separate lines
                                    eds = fields['artists'].split('\n')
                                    try:
                                        with open(artists_file, 'w+') as edfil:
                                            for ed_nick in eds:
                                                ed_nick = ed_nick.strip()
                                                ed_dir = \
                                                    base_dir + \
                                                    '/accounts/' + ed_nick + \
                                                    '@' + domain
                                                if os.path.isdir(ed_dir):
                                                    edfil.write(ed_nick +
                                                                '\n')
                                    except OSError as ex:
                                        print('EX: unable to write artists ' +
                                              artists_file + ' ' + str(ex))

                                    for ed_nick in eds:
                                        ed_nick = ed_nick.strip()
                                        ed_dir = \
                                            base_dir + \
                                            '/accounts/' + \
                                            ed_nick + '@' + \
                                            domain
                                        if os.path.isdir(ed_dir):
                                            set_role(base_dir,
                                                     ed_nick, domain,
                                                     'artist')

                    # remove scheduled posts
                    if fields.get('removeScheduledPosts'):
                        if fields['removeScheduledPosts'] == 'on':
                            remove_scheduled_posts(base_dir,
                                                   nickname, domain)

                    # approve followers
                    if on_final_welcome_screen:
                        # Default setting created via the welcome screen
                        actor_json['manuallyApprovesFollowers'] = True
                        actor_changed = True
                    else:
                        approve_followers = False
                        if fields.get('approveFollowers'):
                            if fields['approveFollowers'] == 'on':
                                approve_followers = True
                        if approve_followers != \
                           actor_json['manuallyApprovesFollowers']:
                            actor_json['manuallyApprovesFollowers'] = \
                                approve_followers
                            actor_changed = True

                    # remove a custom font
                    if fields.get('removeCustomFont'):
                        if (fields['removeCustomFont'] == 'on' and
                            (is_artist(base_dir, nickname) or
                             path.startswith('/users/' +
                                             admin_nickname + '/'))):
                            font_ext = ('woff', 'woff2', 'otf', 'ttf')
                            for ext in font_ext:
                                if os.path.isfile(base_dir +
                                                  '/fonts/custom.' + ext):
                                    try:
                                        os.remove(base_dir +
                                                  '/fonts/custom.' + ext)
                                    except OSError:
                                        print('EX: _profile_edit ' +
                                              'unable to delete ' +
                                              base_dir +
                                              '/fonts/custom.' + ext)
                                if os.path.isfile(base_dir +
                                                  '/fonts/custom.' + ext +
                                                  '.etag'):
                                    try:
                                        os.remove(base_dir +
                                                  '/fonts/custom.' + ext +
                                                  '.etag')
                                    except OSError:
                                        print('EX: _profile_edit ' +
                                              'unable to delete ' +
                                              base_dir + '/fonts/custom.' +
                                              ext + '.etag')
                            curr_theme = get_theme(base_dir)
                            if curr_theme:
                                self.server.theme_name = curr_theme
                                allow_local_network_access = \
                                    self.server.allow_local_network_access
                                set_theme(base_dir, curr_theme, domain,
                                          allow_local_network_access,
                                          system_language,
                                          self.server.dyslexic_font)
                                self.server.text_mode_banner = \
                                    get_text_mode_banner(base_dir)
                                self.server.iconsCache = {}
                                self.server.fontsCache = {}
                                self.server.show_publish_as_icon = \
                                    get_config_param(base_dir,
                                                     'showPublishAsIcon')
                                self.server.full_width_tl_button_header = \
                                    get_config_param(base_dir,
                                                     'fullWidthTimeline' +
                                                     'ButtonHeader')
                                self.server.icons_as_buttons = \
                                    get_config_param(base_dir,
                                                     'iconsAsButtons')
                                self.server.rss_icon_at_top = \
                                    get_config_param(base_dir,
                                                     'rssIconAtTop')
                                self.server.publish_button_at_top = \
                                    get_config_param(base_dir,
                                                     'publishButtonAtTop')

                    # only receive DMs from accounts you follow
                    follow_dms_filename = \
                        acct_dir(base_dir, nickname, domain) + '/.followDMs'
                    if on_final_welcome_screen:
                        # initial default setting created via
                        # the welcome screen
                        try:
                            with open(follow_dms_filename, 'w+') as ffile:
                                ffile.write('\n')
                        except OSError:
                            print('EX: unable to write follow DMs ' +
                                  follow_dms_filename)
                        actor_changed = True
                    else:
                        follow_dms_active = False
                        if fields.get('followDMs'):
                            if fields['followDMs'] == 'on':
                                follow_dms_active = True
                                try:
                                    with open(follow_dms_filename,
                                              'w+') as ffile:
                                        ffile.write('\n')
                                except OSError:
                                    print('EX: unable to write follow DMs 2 ' +
                                          follow_dms_filename)
                        if not follow_dms_active:
                            if os.path.isfile(follow_dms_filename):
                                try:
                                    os.remove(follow_dms_filename)
                                except OSError:
                                    print('EX: _profile_edit ' +
                                          'unable to delete ' +
                                          follow_dms_filename)

                    # remove Twitter retweets
                    remove_twitter_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/.removeTwitter'
                    remove_twitter_active = False
                    if fields.get('removeTwitter'):
                        if fields['removeTwitter'] == 'on':
                            remove_twitter_active = True
                            try:
                                with open(remove_twitter_filename,
                                          'w+') as rfile:
                                    rfile.write('\n')
                            except OSError:
                                print('EX: unable to write remove twitter ' +
                                      remove_twitter_filename)
                    if not remove_twitter_active:
                        if os.path.isfile(remove_twitter_filename):
                            try:
                                os.remove(remove_twitter_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      remove_twitter_filename)

                    # hide Like button
                    hide_like_button_file = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/.hideLikeButton'
                    notify_likes_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/.notifyLikes'
                    hide_like_button_active = False
                    if fields.get('hideLikeButton'):
                        if fields['hideLikeButton'] == 'on':
                            hide_like_button_active = True
                            try:
                                with open(hide_like_button_file, 'w+') as rfil:
                                    rfil.write('\n')
                            except OSError:
                                print('EX: unable to write hide like ' +
                                      hide_like_button_file)
                            # remove notify likes selection
                            if os.path.isfile(notify_likes_filename):
                                try:
                                    os.remove(notify_likes_filename)
                                except OSError:
                                    print('EX: _profile_edit ' +
                                          'unable to delete ' +
                                          notify_likes_filename)
                    if not hide_like_button_active:
                        if os.path.isfile(hide_like_button_file):
                            try:
                                os.remove(hide_like_button_file)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      hide_like_button_file)

                    # hide Reaction button
                    hide_reaction_button_file = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/.hideReactionButton'
                    notify_reactions_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/.notifyReactions'
                    hide_reaction_button_active = False
                    if fields.get('hideReactionButton'):
                        if fields['hideReactionButton'] == 'on':
                            hide_reaction_button_active = True
                            try:
                                with open(hide_reaction_button_file,
                                          'w+') as rfile:
                                    rfile.write('\n')
                            except OSError:
                                print('EX: unable to write hide reaction ' +
                                      hide_reaction_button_file)
                            # remove notify Reaction selection
                            if os.path.isfile(notify_reactions_filename):
                                try:
                                    os.remove(notify_reactions_filename)
                                except OSError:
                                    print('EX: _profile_edit ' +
                                          'unable to delete ' +
                                          notify_reactions_filename)
                    if not hide_reaction_button_active:
                        if os.path.isfile(hide_reaction_button_file):
                            try:
                                os.remove(hide_reaction_button_file)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      hide_reaction_button_file)

                    # notify about new Likes
                    if on_final_welcome_screen:
                        # default setting from welcome screen
                        try:
                            with open(notify_likes_filename, 'w+') as rfile:
                                rfile.write('\n')
                        except OSError:
                            print('EX: unable to write notify likes ' +
                                  notify_likes_filename)
                        actor_changed = True
                    else:
                        notify_likes_active = False
                        if fields.get('notifyLikes'):
                            if fields['notifyLikes'] == 'on' and \
                               not hide_like_button_active:
                                notify_likes_active = True
                                try:
                                    with open(notify_likes_filename,
                                              'w+') as rfile:
                                        rfile.write('\n')
                                except OSError:
                                    print('EX: unable to write notify likes ' +
                                          notify_likes_filename)
                        if not notify_likes_active:
                            if os.path.isfile(notify_likes_filename):
                                try:
                                    os.remove(notify_likes_filename)
                                except OSError:
                                    print('EX: _profile_edit ' +
                                          'unable to delete ' +
                                          notify_likes_filename)

                    notify_reactions_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/.notifyReactions'
                    if on_final_welcome_screen:
                        # default setting from welcome screen
                        notify_react_filename = notify_reactions_filename
                        try:
                            with open(notify_react_filename, 'w+') as rfile:
                                rfile.write('\n')
                        except OSError:
                            print('EX: unable to write notify reactions ' +
                                  notify_reactions_filename)
                        actor_changed = True
                    else:
                        notify_reactions_active = False
                        if fields.get('notifyReactions'):
                            if fields['notifyReactions'] == 'on' and \
                               not hide_reaction_button_active:
                                notify_reactions_active = True
                                try:
                                    with open(notify_reactions_filename,
                                              'w+') as rfile:
                                        rfile.write('\n')
                                except OSError:
                                    print('EX: unable to write ' +
                                          'notify reactions ' +
                                          notify_reactions_filename)
                        if not notify_reactions_active:
                            if os.path.isfile(notify_reactions_filename):
                                try:
                                    os.remove(notify_reactions_filename)
                                except OSError:
                                    print('EX: _profile_edit ' +
                                          'unable to delete ' +
                                          notify_reactions_filename)

                    # this account is a bot
                    if fields.get('isBot'):
                        if fields['isBot'] == 'on':
                            if actor_json['type'] != 'Service':
                                actor_json['type'] = 'Service'
                                actor_changed = True
                    else:
                        # this account is a group
                        if fields.get('isGroup'):
                            if fields['isGroup'] == 'on':
                                if actor_json['type'] != 'Group':
                                    # only allow admin to create groups
                                    if path.startswith('/users/' +
                                                       admin_nickname + '/'):
                                        actor_json['type'] = 'Group'
                                        actor_changed = True
                        else:
                            # this account is a person (default)
                            if actor_json['type'] != 'Person':
                                actor_json['type'] = 'Person'
                                actor_changed = True

                    # grayscale theme
                    if path.startswith('/users/' + admin_nickname + '/') or \
                       is_artist(base_dir, nickname):
                        grayscale = False
                        if fields.get('grayscale'):
                            if fields['grayscale'] == 'on':
                                grayscale = True
                        if grayscale:
                            enable_grayscale(base_dir)
                        else:
                            disable_grayscale(base_dir)

                    # dyslexic font
                    if path.startswith('/users/' + admin_nickname + '/') or \
                       is_artist(base_dir, nickname):
                        dyslexic_font = False
                        if fields.get('dyslexicFont'):
                            if fields['dyslexicFont'] == 'on':
                                dyslexic_font = True
                        if dyslexic_font != self.server.dyslexic_font:
                            self.server.dyslexic_font = dyslexic_font
                            set_config_param(base_dir, 'dyslexicFont',
                                             self.server.dyslexic_font)
                            set_theme(base_dir,
                                      self.server.theme_name,
                                      self.server.domain,
                                      self.server.allow_local_network_access,
                                      self.server.system_language,
                                      self.server.dyslexic_font)

                    # low bandwidth images checkbox
                    if path.startswith('/users/' + admin_nickname + '/') or \
                       is_artist(base_dir, nickname):
                        curr_low_bandwidth = \
                            get_config_param(base_dir, 'lowBandwidth')
                        low_bandwidth = False
                        if fields.get('lowBandwidth'):
                            if fields['lowBandwidth'] == 'on':
                                low_bandwidth = True
                        if curr_low_bandwidth != low_bandwidth:
                            set_config_param(base_dir, 'lowBandwidth',
                                             low_bandwidth)
                            self.server.low_bandwidth = low_bandwidth

                    # save filtered words list
                    filter_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/filters.txt'
                    if fields.get('filteredWords'):
                        try:
                            with open(filter_filename, 'w+') as filterfile:
                                filterfile.write(fields['filteredWords'])
                        except OSError:
                            print('EX: unable to write filter ' +
                                  filter_filename)
                    else:
                        if os.path.isfile(filter_filename):
                            try:
                                os.remove(filter_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete filter ' +
                                      filter_filename)

                    # save filtered words within bio list
                    filter_bio_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/filters_bio.txt'
                    if fields.get('filteredWordsBio'):
                        try:
                            with open(filter_bio_filename, 'w+') as filterfile:
                                filterfile.write(fields['filteredWordsBio'])
                        except OSError:
                            print('EX: unable to write bio filter ' +
                                  filter_bio_filename)
                    else:
                        if os.path.isfile(filter_bio_filename):
                            try:
                                os.remove(filter_bio_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete bio filter ' +
                                      filter_bio_filename)

                    # word replacements
                    switch_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/replacewords.txt'
                    if fields.get('switchwords'):
                        try:
                            with open(switch_filename, 'w+') as switchfile:
                                switchfile.write(fields['switchwords'])
                        except OSError:
                            print('EX: unable to write switches ' +
                                  switch_filename)
                    else:
                        if os.path.isfile(switch_filename):
                            try:
                                os.remove(switch_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      switch_filename)

                    # autogenerated tags
                    auto_tags_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/autotags.txt'
                    if fields.get('autoTags'):
                        try:
                            with open(auto_tags_filename, 'w+') as autofile:
                                autofile.write(fields['autoTags'])
                        except OSError:
                            print('EX: unable to write auto tags ' +
                                  auto_tags_filename)
                    else:
                        if os.path.isfile(auto_tags_filename):
                            try:
                                os.remove(auto_tags_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      auto_tags_filename)

                    # autogenerated content warnings
                    auto_cw_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/autocw.txt'
                    if fields.get('autoCW'):
                        try:
                            with open(auto_cw_filename, 'w+') as auto_cw_file:
                                auto_cw_file.write(fields['autoCW'])
                        except OSError:
                            print('EX: unable to write auto CW ' +
                                  auto_cw_filename)
                    else:
                        if os.path.isfile(auto_cw_filename):
                            try:
                                os.remove(auto_cw_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      auto_cw_filename)

                    # save blocked accounts list
                    blocked_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/blocking.txt'
                    if fields.get('blocked'):
                        try:
                            with open(blocked_filename, 'w+') as blockedfile:
                                blockedfile.write(fields['blocked'])
                        except OSError:
                            print('EX: unable to write blocked accounts ' +
                                  blocked_filename)
                    else:
                        if os.path.isfile(blocked_filename):
                            try:
                                os.remove(blocked_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      blocked_filename)

                    # Save DM allowed instances list.
                    # The allow list for incoming DMs,
                    # if the .followDMs flag file exists
                    dm_allowed_instances_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/dmAllowedinstances.txt'
                    if fields.get('dmAllowedInstances'):
                        try:
                            with open(dm_allowed_instances_filename,
                                      'w+') as afile:
                                afile.write(fields['dmAllowedInstances'])
                        except OSError:
                            print('EX: unable to write allowed DM instances ' +
                                  dm_allowed_instances_filename)
                    else:
                        if os.path.isfile(dm_allowed_instances_filename):
                            try:
                                os.remove(dm_allowed_instances_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      dm_allowed_instances_filename)

                    # save allowed instances list
                    # This is the account level allow list
                    allowed_instances_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/allowedinstances.txt'
                    if fields.get('allowedInstances'):
                        inst_filename = allowed_instances_filename
                        try:
                            with open(inst_filename, 'w+') as afile:
                                afile.write(fields['allowedInstances'])
                        except OSError:
                            print('EX: unable to write allowed instances ' +
                                  allowed_instances_filename)
                    else:
                        if os.path.isfile(allowed_instances_filename):
                            try:
                                os.remove(allowed_instances_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      allowed_instances_filename)

                    if is_moderator(self.server.base_dir, nickname):
                        # set selected content warning lists
                        new_lists_enabled = ''
                        for name, _ in self.server.cw_lists.items():
                            list_var_name = get_cw_list_variable(name)
                            if fields.get(list_var_name):
                                if fields[list_var_name] == 'on':
                                    if new_lists_enabled:
                                        new_lists_enabled += ', ' + name
                                    else:
                                        new_lists_enabled += name
                        if new_lists_enabled != self.server.lists_enabled:
                            self.server.lists_enabled = new_lists_enabled
                            set_config_param(self.server.base_dir,
                                             "listsEnabled",
                                             new_lists_enabled)

                        # save blocked user agents
                        user_agents_blocked = []
                        if fields.get('userAgentsBlockedStr'):
                            user_agents_blocked_str = \
                                fields['userAgentsBlockedStr']
                            user_agents_blocked_list = \
                                user_agents_blocked_str.split('\n')
                            for uagent in user_agents_blocked_list:
                                if uagent in user_agents_blocked:
                                    continue
                                user_agents_blocked.append(uagent.strip())
                        if str(self.server.user_agents_blocked) != \
                           str(user_agents_blocked):
                            self.server.user_agents_blocked = \
                                user_agents_blocked
                            user_agents_blocked_str = ''
                            for uagent in user_agents_blocked:
                                if user_agents_blocked_str:
                                    user_agents_blocked_str += ','
                                user_agents_blocked_str += uagent
                            set_config_param(base_dir, 'userAgentsBlocked',
                                             user_agents_blocked_str)

                        # save peertube instances list
                        peertube_instances_file = \
                            base_dir + '/accounts/peertube.txt'
                        if fields.get('ptInstances'):
                            self.server.peertube_instances.clear()
                            try:
                                with open(peertube_instances_file,
                                          'w+') as afile:
                                    afile.write(fields['ptInstances'])
                            except OSError:
                                print('EX: unable to write peertube ' +
                                      peertube_instances_file)
                            pt_instances_list = \
                                fields['ptInstances'].split('\n')
                            if pt_instances_list:
                                for url in pt_instances_list:
                                    url = url.strip()
                                    if not url:
                                        continue
                                    if url in self.server.peertube_instances:
                                        continue
                                    self.server.peertube_instances.append(url)
                        else:
                            if os.path.isfile(peertube_instances_file):
                                try:
                                    os.remove(peertube_instances_file)
                                except OSError:
                                    print('EX: _profile_edit ' +
                                          'unable to delete ' +
                                          peertube_instances_file)
                            self.server.peertube_instances.clear()

                    # save git project names list
                    git_projects_filename = \
                        acct_dir(base_dir, nickname, domain) + \
                        '/gitprojects.txt'
                    if fields.get('gitProjects'):
                        try:
                            with open(git_projects_filename, 'w+') as afile:
                                afile.write(fields['gitProjects'].lower())
                        except OSError:
                            print('EX: unable to write git ' +
                                  git_projects_filename)
                    else:
                        if os.path.isfile(git_projects_filename):
                            try:
                                os.remove(git_projects_filename)
                            except OSError:
                                print('EX: _profile_edit ' +
                                      'unable to delete ' +
                                      git_projects_filename)

                    # save actor json file within accounts
                    if actor_changed:
                        # update the context for the actor
                        actor_json['@context'] = [
                            'https://www.w3.org/ns/activitystreams',
                            'https://w3id.org/security/v1',
                            get_default_person_context()
                        ]
                        if actor_json.get('nomadicLocations'):
                            del actor_json['nomadicLocations']
                        if not actor_json.get('featured'):
                            actor_json['featured'] = \
                                actor_json['id'] + '/collections/featured'
                        if not actor_json.get('featuredTags'):
                            actor_json['featuredTags'] = \
                                actor_json['id'] + '/collections/tags'
                        randomize_actor_images(actor_json)
                        add_actor_update_timestamp(actor_json)
                        # save the actor
                        save_json(actor_json, actor_filename)
                        webfinger_update(base_dir,
                                         nickname, domain,
                                         onion_domain,
                                         self.server.cached_webfingers)
                        # also copy to the actors cache and
                        # person_cache in memory
                        store_person_in_cache(base_dir,
                                              actor_json['id'], actor_json,
                                              self.server.person_cache,
                                              True)
                        # clear any cached images for this actor
                        id_str = actor_json['id'].replace('/', '-')
                        remove_avatar_from_cache(base_dir, id_str)
                        # save the actor to the cache
                        actor_cache_filename = \
                            base_dir + '/cache/actors/' + \
                            actor_json['id'].replace('/', '#') + '.json'
                        save_json(actor_json, actor_cache_filename)
                        # send profile update to followers
                        update_actor_json = get_actor_update_json(actor_json)
                        print('Sending actor update: ' +
                              str(update_actor_json))
                        self._post_to_outbox(update_actor_json,
                                             self.server.project_version,
                                             nickname)

                    # deactivate the account
                    if fields.get('deactivateThisAccount'):
                        if fields['deactivateThisAccount'] == 'on':
                            deactivate_account(base_dir,
                                               nickname, domain)
                            self._clear_login_details(nickname,
                                                      calling_domain)
                            self.server.postreq_busy = False
                            return

        # redirect back to the profile screen
        self._redirect_headers(actor_str + redirect_path,
                               cookie, calling_domain)
        self.server.postreq_busy = False

    def _progressive_web_app_manifest(self, calling_domain: str,
                                      getreq_start_time) -> None:
        """gets the PWA manifest
        """
        app1 = "https://f-droid.org/en/packages/eu.siacs.conversations"
        app2 = "https://staging.f-droid.org/en/packages/im.vector.app"
        manifest = {
            "name": "Epicyon",
            "short_name": "Epicyon",
            "start_url": "/index.html",
            "display": "standalone",
            "background_color": "black",
            "theme_color": "grey",
            "orientation": "portrait-primary",
            "categories": ["microblog", "fediverse", "activitypub"],
            "screenshots": [
                {
                    "src": "/mobile.jpg",
                    "sizes": "418x851",
                    "type": "image/jpeg"
                },
                {
                    "src": "/mobile_person.jpg",
                    "sizes": "429x860",
                    "type": "image/jpeg"
                },
                {
                    "src": "/mobile_search.jpg",
                    "sizes": "422x861",
                    "type": "image/jpeg"
                }
            ],
            "icons": [
                {
                    "src": "/logo72.png",
                    "type": "image/png",
                    "sizes": "72x72"
                },
                {
                    "src": "/logo96.png",
                    "type": "image/png",
                    "sizes": "96x96"
                },
                {
                    "src": "/logo128.png",
                    "type": "image/png",
                    "sizes": "128x128"
                },
                {
                    "src": "/logo144.png",
                    "type": "image/png",
                    "sizes": "144x144"
                },
                {
                    "src": "/logo150.png",
                    "type": "image/png",
                    "sizes": "150x150"
                },
                {
                    "src": "/apple-touch-icon.png",
                    "type": "image/png",
                    "sizes": "180x180"
                },
                {
                    "src": "/logo192.png",
                    "type": "image/png",
                    "sizes": "192x192"
                },
                {
                    "src": "/logo256.png",
                    "type": "image/png",
                    "sizes": "256x256"
                },
                {
                    "src": "/logo512.png",
                    "type": "image/png",
                    "sizes": "512x512"
                }
            ],
            "related_applications": [
                {
                    "platform": "fdroid",
                    "url": app1
                },
                {
                    "platform": "fdroid",
                    "url": app2
                }
            ]
        }
        msg = json.dumps(manifest,
                         ensure_ascii=False).encode('utf-8')
        msglen = len(msg)
        self._set_headers('application/json', msglen,
                          None, calling_domain, False)
        self._write(msg)
        if self.server.debug:
            print('Sent manifest: ' + calling_domain)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_progressive_web_app_manifest',
                            self.server.debug)

    def _browser_config(self, calling_domain: str, getreq_start_time) -> None:
        """Used by MS Windows to put an icon on the desktop if you
        link to a website
        """
        xml_str = \
            '<?xml version="1.0" encoding="utf-8"?>\n' + \
            '<browserconfig>\n' + \
            '  <msapplication>\n' + \
            '    <tile>\n' + \
            '      <square150x150logo src="/logo150.png"/>\n' + \
            '      <TileColor>#eeeeee</TileColor>\n' + \
            '    </tile>\n' + \
            '  </msapplication>\n' + \
            '</browserconfig>'

        msg = json.dumps(xml_str,
                         ensure_ascii=False).encode('utf-8')
        msglen = len(msg)
        self._set_headers('application/xrd+xml', msglen,
                          None, calling_domain, False)
        self._write(msg)
        if self.server.debug:
            print('Sent browserconfig: ' + calling_domain)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_browser_config',
                            self.server.debug)

    def _get_favicon(self, calling_domain: str,
                     base_dir: str, debug: bool,
                     fav_filename: str) -> None:
        """Return the site favicon or default newswire favicon
        """
        fav_type = 'image/x-icon'
        if self._has_accept(calling_domain):
            if 'image/webp' in self.headers['Accept']:
                fav_type = 'image/webp'
                fav_filename = fav_filename.split('.')[0] + '.webp'
            if 'image/avif' in self.headers['Accept']:
                fav_type = 'image/avif'
                fav_filename = fav_filename.split('.')[0] + '.avif'
        if not self.server.theme_name:
            self.theme_name = get_config_param(base_dir, 'theme')
        if not self.server.theme_name:
            self.server.theme_name = 'default'
        # custom favicon
        favicon_filename = \
            base_dir + '/theme/' + self.server.theme_name + \
            '/icons/' + fav_filename
        if not fav_filename.endswith('.ico'):
            if not os.path.isfile(favicon_filename):
                if fav_filename.endswith('.webp'):
                    fav_filename = fav_filename.replace('.webp', '.ico')
                elif fav_filename.endswith('.avif'):
                    fav_filename = fav_filename.replace('.avif', '.ico')
        if not os.path.isfile(favicon_filename):
            # default favicon
            favicon_filename = \
                base_dir + '/theme/default/icons/' + fav_filename
        if self._etag_exists(favicon_filename):
            # The file has not changed
            if debug:
                print('favicon icon has not changed: ' + calling_domain)
            self._304()
            return
        if self.server.iconsCache.get(fav_filename):
            fav_binary = self.server.iconsCache[fav_filename]
            self._set_headers_etag(favicon_filename,
                                   fav_type,
                                   fav_binary, None,
                                   self.server.domain_full,
                                   False, None)
            self._write(fav_binary)
            if debug:
                print('Sent favicon from cache: ' + calling_domain)
            return
        else:
            if os.path.isfile(favicon_filename):
                fav_binary = None
                try:
                    with open(favicon_filename, 'rb') as fav_file:
                        fav_binary = fav_file.read()
                except OSError:
                    print('EX: unable to read favicon ' + favicon_filename)
                if fav_binary:
                    self._set_headers_etag(favicon_filename,
                                           fav_type,
                                           fav_binary, None,
                                           self.server.domain_full,
                                           False, None)
                    self._write(fav_binary)
                    self.server.iconsCache[fav_filename] = fav_binary
                    if self.server.debug:
                        print('Sent favicon from file: ' + calling_domain)
                    return
        if debug:
            print('favicon not sent: ' + calling_domain)
        self._404()

    def _get_speaker(self, calling_domain: str, path: str,
                     base_dir: str, domain: str, debug: bool) -> None:
        """Returns the speaker file used for TTS and
        accessed via c2s
        """
        nickname = path.split('/users/')[1]
        if '/' in nickname:
            nickname = nickname.split('/')[0]
        speaker_filename = \
            acct_dir(base_dir, nickname, domain) + '/speaker.json'
        if not os.path.isfile(speaker_filename):
            self._404()
            return

        speaker_json = load_json(speaker_filename)
        msg = json.dumps(speaker_json,
                         ensure_ascii=False).encode('utf-8')
        msglen = len(msg)
        self._set_headers('application/json', msglen,
                          None, calling_domain, False)
        self._write(msg)

    def _get_exported_theme(self, calling_domain: str, path: str,
                            base_dir: str, domain_full: str,
                            debug: bool) -> None:
        """Returns an exported theme zip file
        """
        filename = path.split('/exports/', 1)[1]
        filename = base_dir + '/exports/' + filename
        if os.path.isfile(filename):
            export_binary = None
            try:
                with open(filename, 'rb') as fp_exp:
                    export_binary = fp_exp.read()
            except OSError:
                print('EX: unable to read theme export ' + filename)
            if export_binary:
                export_type = 'application/zip'
                self._set_headers_etag(filename, export_type,
                                       export_binary, None,
                                       domain_full, False, None)
                self._write(export_binary)
        self._404()

    def _get_fonts(self, calling_domain: str, path: str,
                   base_dir: str, debug: bool,
                   getreq_start_time) -> None:
        """Returns a font
        """
        font_str = path.split('/fonts/')[1]
        if font_str.endswith('.otf') or \
           font_str.endswith('.ttf') or \
           font_str.endswith('.woff') or \
           font_str.endswith('.woff2'):
            if font_str.endswith('.otf'):
                font_type = 'font/otf'
            elif font_str.endswith('.ttf'):
                font_type = 'font/ttf'
            elif font_str.endswith('.woff'):
                font_type = 'font/woff'
            else:
                font_type = 'font/woff2'
            font_filename = \
                base_dir + '/fonts/' + font_str
            if self._etag_exists(font_filename):
                # The file has not changed
                self._304()
                return
            if self.server.fontsCache.get(font_str):
                font_binary = self.server.fontsCache[font_str]
                self._set_headers_etag(font_filename,
                                       font_type,
                                       font_binary, None,
                                       self.server.domain_full, False, None)
                self._write(font_binary)
                if debug:
                    print('font sent from cache: ' +
                          path + ' ' + calling_domain)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_get_fonts cache',
                                    self.server.debug)
                return
            else:
                if os.path.isfile(font_filename):
                    font_binary = None
                    try:
                        with open(font_filename, 'rb') as fontfile:
                            font_binary = fontfile.read()
                    except OSError:
                        print('EX: unable to load font ' + font_filename)
                    if font_binary:
                        self._set_headers_etag(font_filename,
                                               font_type,
                                               font_binary, None,
                                               self.server.domain_full,
                                               False, None)
                        self._write(font_binary)
                        self.server.fontsCache[font_str] = font_binary
                    if debug:
                        print('font sent from file: ' +
                              path + ' ' + calling_domain)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', '_get_fonts',
                                        self.server.debug)
                    return
        if debug:
            print('font not found: ' + path + ' ' + calling_domain)
        self._404()

    def _get_rss2feed(self, authorized: bool,
                      calling_domain: str, path: str,
                      base_dir: str, http_prefix: str,
                      domain: str, port: int, proxy_type: str,
                      getreq_start_time,
                      debug: bool) -> None:
        """Returns an RSS2 feed for the blog
        """
        nickname = path.split('/blog/')[1]
        if '/' in nickname:
            nickname = nickname.split('/')[0]
        if not nickname.startswith('rss.'):
            account_dir = acct_dir(self.server.base_dir, nickname, domain)
            if os.path.isdir(account_dir):
                if not self._establish_session("RSS request"):
                    return

                msg = \
                    html_blog_page_rss2(authorized,
                                        self.server.session,
                                        base_dir,
                                        http_prefix,
                                        self.server.translate,
                                        nickname,
                                        domain,
                                        port,
                                        MAX_POSTS_IN_RSS_FEED, 1,
                                        True,
                                        self.server.system_language)
                if msg is not None:
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/xml', msglen,
                                      None, calling_domain, True)
                    self._write(msg)
                    if debug:
                        print('Sent rss2 feed: ' +
                              path + ' ' + calling_domain)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', '_get_rss2feed',
                                        debug)
                    return
        if debug:
            print('Failed to get rss2 feed: ' +
                  path + ' ' + calling_domain)
        self._404()

    def _get_rss2site(self, authorized: bool,
                      calling_domain: str, path: str,
                      base_dir: str, http_prefix: str,
                      domain_full: str, port: int, proxy_type: str,
                      translate: {},
                      getreq_start_time,
                      debug: bool) -> None:
        """Returns an RSS2 feed for all blogs on this instance
        """
        if not self._establish_session("get_rss2site"):
            self._404()
            return

        msg = ''
        for _, dirs, _ in os.walk(base_dir + '/accounts'):
            for acct in dirs:
                if not is_account_dir(acct):
                    continue
                nickname = acct.split('@')[0]
                domain = acct.split('@')[1]
                msg += \
                    html_blog_page_rss2(authorized,
                                        self.server.session,
                                        base_dir,
                                        http_prefix,
                                        self.server.translate,
                                        nickname,
                                        domain,
                                        port,
                                        MAX_POSTS_IN_RSS_FEED, 1,
                                        False,
                                        self.server.system_language)
            break
        if msg:
            msg = rss2header(http_prefix,
                             'news', domain_full,
                             'Site', translate) + msg + rss2footer()

            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/xml', msglen,
                              None, calling_domain, True)
            self._write(msg)
            if debug:
                print('Sent rss2 feed: ' +
                      path + ' ' + calling_domain)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_get_rss2site',
                                debug)
            return
        if debug:
            print('Failed to get rss2 feed: ' +
                  path + ' ' + calling_domain)
        self._404()

    def _get_newswire_feed(self, authorized: bool,
                           calling_domain: str, path: str,
                           base_dir: str, http_prefix: str,
                           domain: str, port: int, proxy_type: str,
                           getreq_start_time,
                           debug: bool) -> None:
        """Returns the newswire feed
        """
        if not self._establish_session("get_newswire_feed"):
            self._404()
            return

        msg = get_rs_sfrom_dict(self.server.base_dir, self.server.newswire,
                                self.server.http_prefix,
                                self.server.domain_full,
                                'Newswire', self.server.translate)
        if msg:
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/xml', msglen,
                              None, calling_domain, True)
            self._write(msg)
            if debug:
                print('Sent rss2 newswire feed: ' +
                      path + ' ' + calling_domain)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_get_newswire_feed',
                                debug)
            return
        if debug:
            print('Failed to get rss2 newswire feed: ' +
                  path + ' ' + calling_domain)
        self._404()

    def _get_hashtag_categories_feed(self, authorized: bool,
                                     calling_domain: str, path: str,
                                     base_dir: str, http_prefix: str,
                                     domain: str, port: int, proxy_type: str,
                                     getreq_start_time,
                                     debug: bool) -> None:
        """Returns the hashtag categories feed
        """
        if not self._establish_session("get_hashtag_categories_feed"):
            self._404()
            return

        hashtag_categories = None
        msg = \
            get_hashtag_categories_feed(base_dir, hashtag_categories)
        if msg:
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/xml', msglen,
                              None, calling_domain, True)
            self._write(msg)
            if debug:
                print('Sent rss2 categories feed: ' +
                      path + ' ' + calling_domain)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_get_hashtag_categories_feed', debug)
            return
        if debug:
            print('Failed to get rss2 categories feed: ' +
                  path + ' ' + calling_domain)
        self._404()

    def _get_rss3feed(self, authorized: bool,
                      calling_domain: str, path: str,
                      base_dir: str, http_prefix: str,
                      domain: str, port: int, proxy_type: str,
                      getreq_start_time,
                      debug: bool, system_language: str) -> None:
        """Returns an RSS3 feed
        """
        nickname = path.split('/blog/')[1]
        if '/' in nickname:
            nickname = nickname.split('/')[0]
        if not nickname.startswith('rss.'):
            account_dir = acct_dir(base_dir, nickname, domain)
            if os.path.isdir(account_dir):
                if not self._establish_session("get_rss3feed"):
                    self._404()
                    return
                msg = \
                    html_blog_page_rss3(authorized,
                                        self.server.session,
                                        base_dir, http_prefix,
                                        self.server.translate,
                                        nickname, domain, port,
                                        MAX_POSTS_IN_RSS_FEED, 1,
                                        system_language)
                if msg is not None:
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/plain; charset=utf-8',
                                      msglen, None, calling_domain, True)
                    self._write(msg)
                    if self.server.debug:
                        print('Sent rss3 feed: ' +
                              path + ' ' + calling_domain)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', '_get_rss3feed', debug)
                    return
        if debug:
            print('Failed to get rss3 feed: ' +
                  path + ' ' + calling_domain)
        self._404()

    def _show_person_options(self, calling_domain: str, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str,
                             getreq_start_time,
                             onion_domain: str, i2p_domain: str,
                             cookie: str, debug: bool,
                             authorized: bool) -> None:
        """Show person options screen
        """
        back_to_path = ''
        options_str = path.split('?options=')[1]
        origin_path_str = path.split('?options=')[0]
        if ';' in options_str and '/users/news/' not in path:
            page_number = 1
            options_list = options_str.split(';')
            options_actor = options_list[0]
            options_page_number = options_list[1]
            options_profile_url = options_list[2]
            if '.' in options_profile_url and \
               options_profile_url.startswith('/members/'):
                ext = options_profile_url.split('.')[-1]
                options_profile_url = options_profile_url.split('/members/')[1]
                options_profile_url = \
                    options_profile_url.replace('.' + ext, '')
                options_profile_url = \
                    '/users/' + options_profile_url + '/avatar.' + ext
                back_to_path = 'moderation'
            if options_page_number.isdigit():
                page_number = int(options_page_number)
            options_link = None
            if len(options_list) > 3:
                options_link = options_list[3]
            is_group = False
            donate_url = None
            website_url = None
            enigma_pub_key = None
            pgp_pub_key = None
            pgp_fingerprint = None
            xmpp_address = None
            matrix_address = None
            blog_address = None
            tox_address = None
            briar_address = None
            jami_address = None
            cwtch_address = None
            ssb_address = None
            email_address = None
            locked_account = False
            also_known_as = None
            moved_to = ''
            actor_json = \
                get_person_from_cache(base_dir,
                                      options_actor,
                                      self.server.person_cache,
                                      True)
            if actor_json:
                if actor_json.get('movedTo'):
                    moved_to = actor_json['movedTo']
                    if '"' in moved_to:
                        moved_to = moved_to.split('"')[1]
                if actor_json['type'] == 'Group':
                    is_group = True
                locked_account = get_locked_account(actor_json)
                donate_url = get_donation_url(actor_json)
                website_url = get_website(actor_json, self.server.translate)
                xmpp_address = get_xmpp_address(actor_json)
                matrix_address = get_matrix_address(actor_json)
                ssb_address = get_ssb_address(actor_json)
                blog_address = get_blog_address(actor_json)
                tox_address = get_tox_address(actor_json)
                briar_address = get_briar_address(actor_json)
                jami_address = get_jami_address(actor_json)
                cwtch_address = get_cwtch_address(actor_json)
                email_address = get_email_address(actor_json)
                enigma_pub_key = get_enigma_pub_key(actor_json)
                pgp_pub_key = get_pgp_pub_key(actor_json)
                pgp_fingerprint = get_pgp_fingerprint(actor_json)
                if actor_json.get('alsoKnownAs'):
                    also_known_as = actor_json['alsoKnownAs']

            if self.server.session:
                check_for_changed_actor(self.server.session,
                                        self.server.base_dir,
                                        self.server.http_prefix,
                                        self.server.domain_full,
                                        options_actor, options_profile_url,
                                        self.server.person_cache, 5)

            access_keys = self.server.access_keys
            if '/users/' in path:
                nickname = path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]
            msg = \
                html_person_options(self.server.default_timeline,
                                    self.server.css_cache,
                                    self.server.translate,
                                    base_dir, domain,
                                    domain_full,
                                    origin_path_str,
                                    options_actor,
                                    options_profile_url,
                                    options_link,
                                    page_number, donate_url, website_url,
                                    xmpp_address, matrix_address,
                                    ssb_address, blog_address,
                                    tox_address, briar_address,
                                    jami_address, cwtch_address,
                                    enigma_pub_key,
                                    pgp_pub_key, pgp_fingerprint,
                                    email_address,
                                    self.server.dormant_months,
                                    back_to_path,
                                    locked_account,
                                    moved_to, also_known_as,
                                    self.server.text_mode_banner,
                                    self.server.news_instance,
                                    authorized,
                                    access_keys, is_group).encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_show_person_options', debug)
            return

        if '/users/news/' in path:
            self._redirect_headers(origin_path_str + '/tlfeatures',
                                   cookie, calling_domain)
            return

        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str_absolute = \
                'http://' + onion_domain + origin_path_str
        elif calling_domain.endswith('.i2p') and i2p_domain:
            origin_path_str_absolute = \
                'http://' + i2p_domain + origin_path_str
        else:
            origin_path_str_absolute = \
                http_prefix + '://' + domain_full + origin_path_str
        self._redirect_headers(origin_path_str_absolute, cookie,
                               calling_domain)

    def _show_media(self, calling_domain: str,
                    path: str, base_dir: str,
                    getreq_start_time) -> None:
        """Returns a media file
        """
        if is_image_file(path) or \
           path_is_video(path) or \
           path_is_audio(path):
            media_str = path.split('/media/')[1]
            media_filename = base_dir + '/media/' + media_str
            if os.path.isfile(media_filename):
                if self._etag_exists(media_filename):
                    # The file has not changed
                    self._304()
                    return

                media_file_type = media_file_mime_type(media_filename)

                media_tm = os.path.getmtime(media_filename)
                last_modified_time = datetime.datetime.fromtimestamp(media_tm)
                last_modified_time_str = \
                    last_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

                media_binary = None
                try:
                    with open(media_filename, 'rb') as av_file:
                        media_binary = av_file.read()
                except OSError:
                    print('EX: unable to read media binary ' + media_filename)
                if media_binary:
                    self._set_headers_etag(media_filename, media_file_type,
                                           media_binary, None,
                                           None, True,
                                           last_modified_time_str)
                    self._write(media_binary)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_show_media', self.server.debug)
                return
        self._404()

    def _get_ontology(self, calling_domain: str,
                      path: str, base_dir: str,
                      getreq_start_time) -> None:
        """Returns an ontology file
        """
        if '.owl' in path or '.rdf' in path or '.json' in path:
            if '/ontologies/' in path:
                ontology_str = path.split('/ontologies/')[1].replace('#', '')
            else:
                ontology_str = path.split('/data/')[1].replace('#', '')
            ontology_filename = None
            ontology_file_type = 'application/rdf+xml'
            if ontology_str.startswith('DFC_'):
                ontology_filename = base_dir + '/ontology/DFC/' + ontology_str
            else:
                ontology_str = ontology_str.replace('/data/', '')
                ontology_filename = base_dir + '/ontology/' + ontology_str
            if ontology_str.endswith('.json'):
                ontology_file_type = 'application/ld+json'
            if os.path.isfile(ontology_filename):
                ontology_file = None
                try:
                    with open(ontology_filename, 'r') as fp_ont:
                        ontology_file = fp_ont.read()
                except OSError:
                    print('EX: unable to read ontology ' + ontology_filename)
                if ontology_file:
                    ontology_file = \
                        ontology_file.replace('static.datafoodconsortium.org',
                                              calling_domain)
                    if not calling_domain.endswith('.i2p') and \
                       not calling_domain.endswith('.onion'):
                        ontology_file = \
                            ontology_file.replace('http://' +
                                                  calling_domain,
                                                  'https://' +
                                                  calling_domain)
                    msg = ontology_file.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers(ontology_file_type, msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_get_ontology', self.server.debug)
                return
        self._404()

    def _show_emoji(self, calling_domain: str, path: str,
                    base_dir: str, getreq_start_time) -> None:
        """Returns an emoji image
        """
        if is_image_file(path):
            emoji_str = path.split('/emoji/')[1]
            emoji_filename = base_dir + '/emoji/' + emoji_str
            if not os.path.isfile(emoji_filename):
                emoji_filename = base_dir + '/emojicustom/' + emoji_str
            if os.path.isfile(emoji_filename):
                if self._etag_exists(emoji_filename):
                    # The file has not changed
                    self._304()
                    return

                media_image_type = get_image_mime_type(emoji_filename)
                media_binary = None
                try:
                    with open(emoji_filename, 'rb') as av_file:
                        media_binary = av_file.read()
                except OSError:
                    print('EX: unable to read emoji image ' + emoji_filename)
                if media_binary:
                    self._set_headers_etag(emoji_filename,
                                           media_image_type,
                                           media_binary, None,
                                           self.server.domain_full,
                                           False, None)
                    self._write(media_binary)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_show_emoji', self.server.debug)
                return
        self._404()

    def _show_icon(self, calling_domain: str, path: str,
                   base_dir: str, getreq_start_time) -> None:
        """Shows an icon
        """
        if not path.endswith('.png'):
            self._404()
            return
        media_str = path.split('/icons/')[1]
        if '/' not in media_str:
            if not self.server.theme_name:
                theme = 'default'
            else:
                theme = self.server.theme_name
            icon_filename = media_str
        else:
            theme = media_str.split('/')[0]
            icon_filename = media_str.split('/')[1]
        media_filename = \
            base_dir + '/theme/' + theme + '/icons/' + icon_filename
        if self._etag_exists(media_filename):
            # The file has not changed
            self._304()
            return
        if self.server.iconsCache.get(media_str):
            media_binary = self.server.iconsCache[media_str]
            mime_type_str = media_file_mime_type(media_filename)
            self._set_headers_etag(media_filename,
                                   mime_type_str,
                                   media_binary, None,
                                   self.server.domain_full,
                                   False, None)
            self._write(media_binary)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_show_icon', self.server.debug)
            return
        else:
            if os.path.isfile(media_filename):
                media_binary = None
                try:
                    with open(media_filename, 'rb') as av_file:
                        media_binary = av_file.read()
                except OSError:
                    print('EX: unable to read icon image ' + media_filename)
                if media_binary:
                    mime_type = media_file_mime_type(media_filename)
                    self._set_headers_etag(media_filename,
                                           mime_type,
                                           media_binary, None,
                                           self.server.domain_full,
                                           False, None)
                    self._write(media_binary)
                    self.server.iconsCache[media_str] = media_binary
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_show_icon', self.server.debug)
                return
        self._404()

    def _show_help_screen_image(self, calling_domain: str, path: str,
                                base_dir: str, getreq_start_time) -> None:
        """Shows a help screen image
        """
        if not is_image_file(path):
            return
        media_str = path.split('/helpimages/')[1]
        if '/' not in media_str:
            if not self.server.theme_name:
                theme = 'default'
            else:
                theme = self.server.theme_name
            icon_filename = media_str
        else:
            theme = media_str.split('/')[0]
            icon_filename = media_str.split('/')[1]
        media_filename = \
            base_dir + '/theme/' + theme + '/helpimages/' + icon_filename
        # if there is no theme-specific help image then use the default one
        if not os.path.isfile(media_filename):
            media_filename = \
                base_dir + '/theme/default/helpimages/' + icon_filename
        if self._etag_exists(media_filename):
            # The file has not changed
            self._304()
            return
        if os.path.isfile(media_filename):
            media_binary = None
            try:
                with open(media_filename, 'rb') as av_file:
                    media_binary = av_file.read()
            except OSError:
                print('EX: unable to read help image ' + media_filename)
            if media_binary:
                mime_type = media_file_mime_type(media_filename)
                self._set_headers_etag(media_filename,
                                       mime_type,
                                       media_binary, None,
                                       self.server.domain_full,
                                       False, None)
                self._write(media_binary)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_show_help_screen_image',
                                self.server.debug)
            return
        self._404()

    def _show_cached_favicon(self, referer_domain: str, path: str,
                             base_dir: str, getreq_start_time) -> None:
        """Shows a favicon image obtained from the cache
        """
        fav_file = path.replace('/favicons/', '')
        fav_filename = base_dir + urllib.parse.unquote_plus(path)
        print('showCachedFavicon: ' + fav_filename)
        if self.server.favicons_cache.get(fav_file):
            media_binary = self.server.favicons_cache[fav_file]
            mime_type = media_file_mime_type(fav_filename)
            self._set_headers_etag(fav_filename,
                                   mime_type,
                                   media_binary, None,
                                   referer_domain,
                                   False, None)
            self._write(media_binary)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_show_cached_favicon2',
                                self.server.debug)
            return
        if not os.path.isfile(fav_filename):
            self._404()
            return
        if self._etag_exists(fav_filename):
            # The file has not changed
            self._304()
            return
        media_binary = None
        try:
            with open(fav_filename, 'rb') as av_file:
                media_binary = av_file.read()
        except OSError:
            print('EX: unable to read cached favicon ' + fav_filename)
        if media_binary:
            mime_type = media_file_mime_type(fav_filename)
            self._set_headers_etag(fav_filename,
                                   mime_type,
                                   media_binary, None,
                                   referer_domain,
                                   False, None)
            self._write(media_binary)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_show_cached_favicon',
                                self.server.debug)
            self.server.favicons_cache[fav_file] = media_binary
            return
        self._404()

    def _show_cached_avatar(self, referer_domain: str, path: str,
                            base_dir: str, getreq_start_time) -> None:
        """Shows an avatar image obtained from the cache
        """
        media_filename = base_dir + '/cache' + path
        if os.path.isfile(media_filename):
            if self._etag_exists(media_filename):
                # The file has not changed
                self._304()
                return
            media_binary = None
            try:
                with open(media_filename, 'rb') as av_file:
                    media_binary = av_file.read()
            except OSError:
                print('EX: unable to read cached avatar ' + media_filename)
            if media_binary:
                mime_type = media_file_mime_type(media_filename)
                self._set_headers_etag(media_filename,
                                       mime_type,
                                       media_binary, None,
                                       referer_domain,
                                       False, None)
                self._write(media_binary)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_show_cached_avatar',
                                    self.server.debug)
                return
        self._404()

    def _hashtag_search(self, calling_domain: str,
                        path: str, cookie: str,
                        base_dir: str, http_prefix: str,
                        domain: str, domain_full: str, port: int,
                        onion_domain: str, i2p_domain: str,
                        getreq_start_time) -> None:
        """Return the result of a hashtag search
        """
        page_number = 1
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        hashtag = path.split('/tags/')[1]
        if '?page=' in hashtag:
            hashtag = hashtag.split('?page=')[0]
        hashtag = urllib.parse.unquote_plus(hashtag)
        if is_blocked_hashtag(base_dir, hashtag):
            print('BLOCK: hashtag #' + hashtag)
            msg = html_hashtag_blocked(self.server.css_cache, base_dir,
                                       self.server.translate).encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html', msglen, calling_domain)
            self._write(msg)
            return
        nickname = None
        if '/users/' in path:
            nickname = path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            if '?' in nickname:
                nickname = nickname.split('?')[0]
        hashtag_str = \
            html_hashtag_search(self.server.css_cache,
                                nickname, domain, port,
                                self.server.recent_posts_cache,
                                self.server.max_recent_posts,
                                self.server.translate,
                                base_dir, hashtag, page_number,
                                MAX_POSTS_IN_HASHTAG_FEED, self.server.session,
                                self.server.cached_webfingers,
                                self.server.person_cache,
                                http_prefix,
                                self.server.project_version,
                                self.server.yt_replace_domain,
                                self.server.twitter_replacement_domain,
                                self.server.show_published_date_only,
                                self.server.peertube_instances,
                                self.server.allow_local_network_access,
                                self.server.theme_name,
                                self.server.system_language,
                                self.server.max_like_count,
                                self.server.signing_priv_key_pem,
                                self.server.cw_lists,
                                self.server.lists_enabled)
        if hashtag_str:
            msg = hashtag_str.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
        else:
            origin_path_str = path.split('/tags/')[0]
            origin_path_str_absolute = \
                http_prefix + '://' + domain_full + origin_path_str
            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str_absolute = \
                    'http://' + onion_domain + origin_path_str
            elif (calling_domain.endswith('.i2p') and onion_domain):
                origin_path_str_absolute = \
                    'http://' + i2p_domain + origin_path_str
            self._redirect_headers(origin_path_str_absolute + '/search',
                                   cookie, calling_domain)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_hashtag_search',
                            self.server.debug)

    def _hashtag_search_rss2(self, calling_domain: str,
                             path: str, cookie: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time) -> None:
        """Return an RSS 2 feed for a hashtag
        """
        hashtag = path.split('/tags/rss2/')[1]
        if is_blocked_hashtag(base_dir, hashtag):
            self._400()
            return
        nickname = None
        if '/users/' in path:
            actor = \
                http_prefix + '://' + domain_full + path
            nickname = \
                get_nickname_from_actor(actor)
        hashtag_str = \
            rss_hashtag_search(nickname,
                               domain, port,
                               self.server.recent_posts_cache,
                               self.server.max_recent_posts,
                               self.server.translate,
                               base_dir, hashtag,
                               MAX_POSTS_IN_FEED, self.server.session,
                               self.server.cached_webfingers,
                               self.server.person_cache,
                               http_prefix,
                               self.server.project_version,
                               self.server.yt_replace_domain,
                               self.server.twitter_replacement_domain,
                               self.server.system_language)
        if hashtag_str:
            msg = hashtag_str.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/xml', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
        else:
            origin_path_str = path.split('/tags/rss2/')[0]
            origin_path_str_absolute = \
                http_prefix + '://' + domain_full + origin_path_str
            if calling_domain.endswith('.onion') and onion_domain:
                origin_path_str_absolute = \
                    'http://' + onion_domain + origin_path_str
            elif (calling_domain.endswith('.i2p') and onion_domain):
                origin_path_str_absolute = \
                    'http://' + i2p_domain + origin_path_str
            self._redirect_headers(origin_path_str_absolute + '/search',
                                   cookie, calling_domain)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_hashtag_search_rss2',
                            self.server.debug)

    def _announce_button(self, calling_domain: str, path: str,
                         base_dir: str,
                         cookie: str, proxy_type: str,
                         http_prefix: str,
                         domain: str, domain_full: str, port: int,
                         onion_domain: str, i2p_domain: str,
                         getreq_start_time,
                         repeat_private: bool,
                         debug: bool) -> None:
        """The announce/repeat button was pressed on a post
        """
        page_number = 1
        repeat_url = path.split('?repeat=')[1]
        if '?' in repeat_url:
            repeat_url = repeat_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        actor = path.split('?repeat=')[0]
        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number)
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        if not self._establish_session("announceButton"):
            self._404()
            return
        self.server.actorRepeat = path.split('?actor=')[1]
        announce_to_str = \
            local_actor_url(http_prefix, self.post_to_nickname,
                            domain_full) + \
            '/followers'
        if not repeat_private:
            announce_to_str = 'https://www.w3.org/ns/activitystreams#Public'
        announce_json = \
            create_announce(self.server.session,
                            base_dir,
                            self.server.federation_list,
                            self.post_to_nickname,
                            domain, port,
                            announce_to_str,
                            None, http_prefix,
                            repeat_url, False, False,
                            self.server.send_threads,
                            self.server.postLog,
                            self.server.person_cache,
                            self.server.cached_webfingers,
                            debug,
                            self.server.project_version,
                            self.server.signing_priv_key_pem)
        announce_filename = None
        if announce_json:
            # save the announce straight to the outbox
            # This is because the subsequent send is within a separate thread
            # but the html still needs to be generated before this call ends
            announce_id = remove_id_ending(announce_json['id'])
            announce_filename = \
                save_post_to_box(base_dir, http_prefix, announce_id,
                                 self.post_to_nickname, domain_full,
                                 announce_json, 'outbox')

            # clear the icon from the cache so that it gets updated
            if self.server.iconsCache.get('repeat.png'):
                del self.server.iconsCache['repeat.png']

            # send out the announce within a separate thread
            self._post_to_outbox(announce_json,
                                 self.server.project_version,
                                 self.post_to_nickname)

            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_announce_button postToOutboxThread',
                                self.server.debug)

        # generate the html for the announce
        if announce_json and announce_filename:
            if debug:
                print('Generating html post for announce')
            cached_post_filename = \
                get_cached_post_filename(base_dir, self.post_to_nickname,
                                         domain, announce_json)
            if debug:
                print('Announced post json: ' + str(announce_json))
                print('Announced post nickname: ' +
                      self.post_to_nickname + ' ' + domain)
                print('Announced post cache: ' + str(cached_post_filename))
            show_individual_post_icons = True
            manually_approve_followers = \
                follower_approval_active(base_dir,
                                         self.post_to_nickname, domain)
            show_repeats = not is_dm(announce_json)
            individual_post_as_html(self.server.signing_priv_key_pem, False,
                                    self.server.recent_posts_cache,
                                    self.server.max_recent_posts,
                                    self.server.translate,
                                    page_number, base_dir,
                                    self.server.session,
                                    self.server.cached_webfingers,
                                    self.server.person_cache,
                                    self.post_to_nickname, domain,
                                    self.server.port, announce_json,
                                    None, True,
                                    self.server.allow_deletion,
                                    http_prefix, self.server.project_version,
                                    timeline_str,
                                    self.server.yt_replace_domain,
                                    self.server.twitter_replacement_domain,
                                    self.server.show_published_date_only,
                                    self.server.peertube_instances,
                                    self.server.allow_local_network_access,
                                    self.server.theme_name,
                                    self.server.system_language,
                                    self.server.max_like_count,
                                    show_repeats,
                                    show_individual_post_icons,
                                    manually_approve_followers,
                                    False, True, False,
                                    self.server.cw_lists,
                                    self.server.lists_enabled)

        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + '?page=' + \
            str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_announce_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie, calling_domain)

    def _undo_announce_button(self, calling_domain: str, path: str,
                              base_dir: str,
                              cookie: str, proxy_type: str,
                              http_prefix: str,
                              domain: str, domain_full: str, port: int,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              repeat_private: bool, debug: bool,
                              recent_posts_cache: {}) -> None:
        """Undo announce/repeat button was pressed
        """
        page_number = 1

        # the post which was referenced by the announce post
        repeat_url = path.split('?unrepeat=')[1]
        if '?' in repeat_url:
            repeat_url = repeat_url.split('?')[0]

        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        actor = path.split('?unrepeat=')[0]
        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + '?page=' + \
                str(page_number)
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        if not self._establish_session("undoAnnounceButton"):
            self._404()
            return
        undo_announce_actor = \
            http_prefix + '://' + domain_full + \
            '/users/' + self.post_to_nickname
        un_repeat_to_str = 'https://www.w3.org/ns/activitystreams#Public'
        new_undo_announce = {
            "@context": "https://www.w3.org/ns/activitystreams",
            'actor': undo_announce_actor,
            'type': 'Undo',
            'cc': [undo_announce_actor + '/followers'],
            'to': [un_repeat_to_str],
            'object': {
                'actor': undo_announce_actor,
                'cc': [undo_announce_actor + '/followers'],
                'object': repeat_url,
                'to': [un_repeat_to_str],
                'type': 'Announce'
            }
        }
        # clear the icon from the cache so that it gets updated
        if self.server.iconsCache.get('repeat_inactive.png'):
            del self.server.iconsCache['repeat_inactive.png']

        # delete  the announce post
        if '?unannounce=' in path:
            announce_url = path.split('?unannounce=')[1]
            if '?' in announce_url:
                announce_url = announce_url.split('?')[0]
            post_filename = None
            nickname = get_nickname_from_actor(announce_url)
            if nickname:
                if domain_full + '/users/' + nickname + '/' in announce_url:
                    post_filename = \
                        locate_post(base_dir, nickname, domain, announce_url)
            if post_filename:
                delete_post(base_dir, http_prefix,
                            nickname, domain, post_filename,
                            debug, recent_posts_cache)

        self._post_to_outbox(new_undo_announce,
                             self.server.project_version,
                             self.post_to_nickname)

        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + '?page=' + \
            str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_undo_announce_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie, calling_domain)

    def _follow_approve_button(self, calling_domain: str, path: str,
                               cookie: str,
                               base_dir: str, http_prefix: str,
                               domain: str, domain_full: str, port: int,
                               onion_domain: str, i2p_domain: str,
                               getreq_start_time,
                               proxy_type: str, debug: bool) -> None:
        """Follow approve button was pressed
        """
        origin_path_str = path.split('/followapprove=')[0]
        follower_nickname = origin_path_str.replace('/users/', '')
        following_handle = path.split('/followapprove=')[1]
        if '://' in following_handle:
            handle_nickname = get_nickname_from_actor(following_handle)
            handle_domain, handle_port = \
                get_domain_from_actor(following_handle)
            following_handle = \
                handle_nickname + '@' + \
                get_full_domain(handle_domain, handle_port)
        if '@' in following_handle:
            if not self._establish_session("followApproveButton"):
                self._404()
                return
            signing_priv_key_pem = \
                self.server.signing_priv_key_pem
            manual_approve_follow_request_thread(self.server.session,
                                                 base_dir, http_prefix,
                                                 follower_nickname,
                                                 domain, port,
                                                 following_handle,
                                                 self.server.federation_list,
                                                 self.server.send_threads,
                                                 self.server.postLog,
                                                 self.server.cached_webfingers,
                                                 self.server.person_cache,
                                                 debug,
                                                 self.server.project_version,
                                                 signing_priv_key_pem)
        origin_path_str_absolute = \
            http_prefix + '://' + domain_full + origin_path_str
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str_absolute = \
                'http://' + onion_domain + origin_path_str
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str_absolute = \
                'http://' + i2p_domain + origin_path_str
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_follow_approve_button',
                            self.server.debug)
        self._redirect_headers(origin_path_str_absolute,
                               cookie, calling_domain)

    def _newswire_vote(self, calling_domain: str, path: str,
                       cookie: str,
                       base_dir: str, http_prefix: str,
                       domain: str, domain_full: str, port: int,
                       onion_domain: str, i2p_domain: str,
                       getreq_start_time,
                       proxy_type: str, debug: bool,
                       newswire: {}):
        """Vote for a newswire item
        """
        origin_path_str = path.split('/newswirevote=')[0]
        date_str = \
            path.split('/newswirevote=')[1].replace('T', ' ')
        date_str = date_str.replace(' 00:00', '').replace('+00:00', '')
        date_str = urllib.parse.unquote_plus(date_str) + '+00:00'
        nickname = \
            urllib.parse.unquote_plus(origin_path_str.split('/users/')[1])
        if '/' in nickname:
            nickname = nickname.split('/')[0]
        print('Newswire item date: ' + date_str)
        if newswire.get(date_str):
            if is_moderator(base_dir, nickname):
                newswire_item = newswire[date_str]
                print('Voting on newswire item: ' + str(newswire_item))
                votes_index = 2
                filename_index = 3
                if 'vote:' + nickname not in newswire_item[votes_index]:
                    newswire_item[votes_index].append('vote:' + nickname)
                    filename = newswire_item[filename_index]
                    newswire_state_filename = \
                        base_dir + '/accounts/.newswirestate.json'
                    try:
                        save_json(newswire, newswire_state_filename)
                    except BaseException as ex:
                        print('EX: saving newswire state, ' + str(ex))
                    if filename:
                        save_json(newswire_item[votes_index],
                                  filename + '.votes')
        else:
            print('No newswire item with date: ' + date_str + ' ' +
                  str(newswire))

        origin_path_str_absolute = \
            http_prefix + '://' + domain_full + origin_path_str + '/' + \
            self.server.default_timeline
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str_absolute = \
                'http://' + onion_domain + origin_path_str
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str_absolute = \
                'http://' + i2p_domain + origin_path_str
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_newswire_vote',
                            self.server.debug)
        self._redirect_headers(origin_path_str_absolute,
                               cookie, calling_domain)

    def _newswire_unvote(self, calling_domain: str, path: str,
                         cookie: str,
                         base_dir: str, http_prefix: str,
                         domain: str, domain_full: str, port: int,
                         onion_domain: str, i2p_domain: str,
                         getreq_start_time,
                         proxy_type: str, debug: bool,
                         newswire: {}):
        """Remove vote for a newswire item
        """
        origin_path_str = path.split('/newswireunvote=')[0]
        date_str = \
            path.split('/newswireunvote=')[1].replace('T', ' ')
        date_str = date_str.replace(' 00:00', '').replace('+00:00', '')
        date_str = urllib.parse.unquote_plus(date_str) + '+00:00'
        nickname = \
            urllib.parse.unquote_plus(origin_path_str.split('/users/')[1])
        if '/' in nickname:
            nickname = nickname.split('/')[0]
        if newswire.get(date_str):
            if is_moderator(base_dir, nickname):
                votes_index = 2
                filename_index = 3
                newswire_item = newswire[date_str]
                if 'vote:' + nickname in newswire_item[votes_index]:
                    newswire_item[votes_index].remove('vote:' + nickname)
                    filename = newswire_item[filename_index]
                    newswire_state_filename = \
                        base_dir + '/accounts/.newswirestate.json'
                    try:
                        save_json(newswire, newswire_state_filename)
                    except BaseException as ex:
                        print('EX: saving newswire state, ' + str(ex))
                    if filename:
                        save_json(newswire_item[votes_index],
                                  filename + '.votes')
        else:
            print('No newswire item with date: ' + date_str + ' ' +
                  str(newswire))

        origin_path_str_absolute = \
            http_prefix + '://' + domain_full + origin_path_str + '/' + \
            self.server.default_timeline
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str_absolute = \
                'http://' + onion_domain + origin_path_str
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            origin_path_str_absolute = \
                'http://' + i2p_domain + origin_path_str
        self._redirect_headers(origin_path_str_absolute,
                               cookie, calling_domain)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_newswire_unvote',
                            self.server.debug)

    def _follow_deny_button(self, calling_domain: str, path: str,
                            cookie: str,
                            base_dir: str, http_prefix: str,
                            domain: str, domain_full: str, port: int,
                            onion_domain: str, i2p_domain: str,
                            getreq_start_time,
                            proxy_type: str, debug: bool) -> None:
        """Follow deny button was pressed
        """
        origin_path_str = path.split('/followdeny=')[0]
        follower_nickname = origin_path_str.replace('/users/', '')
        following_handle = path.split('/followdeny=')[1]
        if '://' in following_handle:
            handle_nickname = get_nickname_from_actor(following_handle)
            handle_domain, handle_port = \
                get_domain_from_actor(following_handle)
            following_handle = \
                handle_nickname + '@' + \
                get_full_domain(handle_domain, handle_port)
        if '@' in following_handle:
            manual_deny_follow_request_thread(self.server.session,
                                              base_dir, http_prefix,
                                              follower_nickname,
                                              domain, port,
                                              following_handle,
                                              self.server.federation_list,
                                              self.server.send_threads,
                                              self.server.postLog,
                                              self.server.cached_webfingers,
                                              self.server.person_cache,
                                              debug,
                                              self.server.project_version,
                                              self.server.signing_priv_key_pem)
        origin_path_str_absolute = \
            http_prefix + '://' + domain_full + origin_path_str
        if calling_domain.endswith('.onion') and onion_domain:
            origin_path_str_absolute = \
                'http://' + onion_domain + origin_path_str
        elif calling_domain.endswith('.i2p') and i2p_domain:
            origin_path_str_absolute = \
                'http://' + i2p_domain + origin_path_str
        self._redirect_headers(origin_path_str_absolute,
                               cookie, calling_domain)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_follow_deny_button',
                            self.server.debug)

    def _like_button(self, calling_domain: str, path: str,
                     base_dir: str, http_prefix: str,
                     domain: str, domain_full: str,
                     onion_domain: str, i2p_domain: str,
                     getreq_start_time,
                     proxy_type: str, cookie: str,
                     debug: str) -> None:
        """Press the like button
        """
        page_number = 1
        like_url = path.split('?like=')[1]
        if '?' in like_url:
            like_url = like_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        actor = path.split('?like=')[0]
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]

        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number) + timeline_bookmark
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        if not self._establish_session("likeButton"):
            self._404()
            return
        like_actor = \
            local_actor_url(http_prefix, self.post_to_nickname, domain_full)
        actor_liked = path.split('?actor=')[1]
        if '?' in actor_liked:
            actor_liked = actor_liked.split('?')[0]

        # if this is an announce then send the like to the original post
        orig_actor, orig_post_url, orig_filename = \
            get_original_post_from_announce_url(like_url, base_dir,
                                                self.post_to_nickname, domain)
        like_url2 = like_url
        liked_post_filename = orig_filename
        if orig_actor and orig_post_url:
            actor_liked = orig_actor
            like_url2 = orig_post_url
            liked_post_filename = None

        like_json = {
            "@context": "https://www.w3.org/ns/activitystreams",
            'type': 'Like',
            'actor': like_actor,
            'to': [actor_liked],
            'object': like_url2
        }

        # send out the like to followers
        self._post_to_outbox(like_json, self.server.project_version, None)

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_like_button postToOutbox',
                            self.server.debug)

        print('Locating liked post ' + like_url)
        # directly like the post file
        if not liked_post_filename:
            liked_post_filename = \
                locate_post(base_dir, self.post_to_nickname, domain, like_url)
        if liked_post_filename:
            recent_posts_cache = self.server.recent_posts_cache
            liked_post_json = load_json(liked_post_filename, 0, 1)
            if orig_filename and orig_post_url:
                update_likes_collection(recent_posts_cache,
                                        base_dir, liked_post_filename,
                                        like_url, like_actor,
                                        self.post_to_nickname,
                                        domain, debug, liked_post_json)
                like_url = orig_post_url
                liked_post_filename = orig_filename
            if debug:
                print('Updating likes for ' + liked_post_filename)
            update_likes_collection(recent_posts_cache,
                                    base_dir, liked_post_filename, like_url,
                                    like_actor, self.post_to_nickname, domain,
                                    debug, None)
            if debug:
                print('Regenerating html post for changed likes collection')
            # clear the icon from the cache so that it gets updated
            if liked_post_json:
                cached_post_filename = \
                    get_cached_post_filename(base_dir, self.post_to_nickname,
                                             domain, liked_post_json)
                if debug:
                    print('Liked post json: ' + str(liked_post_json))
                    print('Liked post nickname: ' +
                          self.post_to_nickname + ' ' + domain)
                    print('Liked post cache: ' + str(cached_post_filename))
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir,
                                             self.post_to_nickname, domain)
                show_repeats = not is_dm(liked_post_json)
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        False,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        self.post_to_nickname, domain,
                                        self.server.port, liked_post_json,
                                        None, True,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        False, True, False,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Liked post not found: ' + liked_post_filename)
            # clear the icon from the cache so that it gets updated
            if self.server.iconsCache.get('like.png'):
                del self.server.iconsCache['like.png']
        else:
            print('WARN: unable to locate file for liked post ' +
                  like_url)

        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + \
            '?page=' + str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_like_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie,
                               calling_domain)

    def _undo_like_button(self, calling_domain: str, path: str,
                          base_dir: str, http_prefix: str,
                          domain: str, domain_full: str,
                          onion_domain: str, i2p_domain: str,
                          getreq_start_time,
                          proxy_type: str, cookie: str,
                          debug: str) -> None:
        """A button is pressed to undo
        """
        page_number = 1
        like_url = path.split('?unlike=')[1]
        if '?' in like_url:
            like_url = like_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        actor = path.split('?unlike=')[0]
        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number)
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        if not self._establish_session("undoLikeButton"):
            self._404()
            return
        undo_actor = \
            local_actor_url(http_prefix, self.post_to_nickname, domain_full)
        actor_liked = path.split('?actor=')[1]
        if '?' in actor_liked:
            actor_liked = actor_liked.split('?')[0]

        # if this is an announce then send the like to the original post
        orig_actor, orig_post_url, orig_filename = \
            get_original_post_from_announce_url(like_url, base_dir,
                                                self.post_to_nickname, domain)
        like_url2 = like_url
        liked_post_filename = orig_filename
        if orig_actor and orig_post_url:
            actor_liked = orig_actor
            like_url2 = orig_post_url
            liked_post_filename = None

        undo_like_json = {
            "@context": "https://www.w3.org/ns/activitystreams",
            'type': 'Undo',
            'actor': undo_actor,
            'to': [actor_liked],
            'object': {
                'type': 'Like',
                'actor': undo_actor,
                'to': [actor_liked],
                'object': like_url2
            }
        }

        # send out the undo like to followers
        self._post_to_outbox(undo_like_json,
                             self.server.project_version, None)

        # directly undo the like within the post file
        if not liked_post_filename:
            liked_post_filename = locate_post(base_dir, self.post_to_nickname,
                                              domain, like_url)
        if liked_post_filename:
            recent_posts_cache = self.server.recent_posts_cache
            liked_post_json = load_json(liked_post_filename, 0, 1)
            if orig_filename and orig_post_url:
                undo_likes_collection_entry(recent_posts_cache,
                                            base_dir, liked_post_filename,
                                            like_url, undo_actor,
                                            domain, debug,
                                            liked_post_json)
                like_url = orig_post_url
                liked_post_filename = orig_filename
            if debug:
                print('Removing likes for ' + liked_post_filename)
            undo_likes_collection_entry(recent_posts_cache,
                                        base_dir,
                                        liked_post_filename, like_url,
                                        undo_actor, domain, debug, None)
            if debug:
                print('Regenerating html post for changed likes collection')
            if liked_post_json:
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir,
                                             self.post_to_nickname, domain)
                show_repeats = not is_dm(liked_post_json)
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        False,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        self.post_to_nickname, domain,
                                        self.server.port, liked_post_json,
                                        None, True,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        False, True, False,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Unliked post not found: ' + liked_post_filename)
            # clear the icon from the cache so that it gets updated
            if self.server.iconsCache.get('like_inactive.png'):
                del self.server.iconsCache['like_inactive.png']
        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + \
            '?page=' + str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_undo_like_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie,
                               calling_domain)

    def _reaction_button(self, calling_domain: str, path: str,
                         base_dir: str, http_prefix: str,
                         domain: str, domain_full: str,
                         onion_domain: str, i2p_domain: str,
                         getreq_start_time,
                         proxy_type: str, cookie: str,
                         debug: str) -> None:
        """Press an emoji reaction button
        Note that this is not the emoji reaction selection icon at the
        bottom of the post
        """
        page_number = 1
        reaction_url = path.split('?react=')[1]
        if '?' in reaction_url:
            reaction_url = reaction_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        actor = path.split('?react=')[0]
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        emoji_content_encoded = None
        if '?emojreact=' in path:
            emoji_content_encoded = path.split('?emojreact=')[1]
            if '?' in emoji_content_encoded:
                emoji_content_encoded = emoji_content_encoded.split('?')[0]
        if not emoji_content_encoded:
            print('WARN: no emoji reaction ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number) + timeline_bookmark
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        emoji_content = urllib.parse.unquote_plus(emoji_content_encoded)
        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number) + timeline_bookmark
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        if not self._establish_session("reactionButton"):
            self._404()
            return
        reaction_actor = \
            local_actor_url(http_prefix, self.post_to_nickname, domain_full)
        actor_reaction = path.split('?actor=')[1]
        if '?' in actor_reaction:
            actor_reaction = actor_reaction.split('?')[0]

        # if this is an announce then send the emoji reaction
        # to the original post
        orig_actor, orig_post_url, orig_filename = \
            get_original_post_from_announce_url(reaction_url, base_dir,
                                                self.post_to_nickname, domain)
        reaction_url2 = reaction_url
        reaction_post_filename = orig_filename
        if orig_actor and orig_post_url:
            actor_reaction = orig_actor
            reaction_url2 = orig_post_url
            reaction_post_filename = None

        reaction_json = {
            "@context": "https://www.w3.org/ns/activitystreams",
            'type': 'EmojiReact',
            'actor': reaction_actor,
            'to': [actor_reaction],
            'object': reaction_url2,
            'content': emoji_content
        }

        # send out the emoji reaction to followers
        self._post_to_outbox(reaction_json, self.server.project_version, None)

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_reaction_button postToOutbox',
                            self.server.debug)

        print('Locating emoji reaction post ' + reaction_url)
        # directly emoji reaction the post file
        if not reaction_post_filename:
            reaction_post_filename = \
                locate_post(base_dir, self.post_to_nickname, domain,
                            reaction_url)
        if reaction_post_filename:
            recent_posts_cache = self.server.recent_posts_cache
            reaction_post_json = load_json(reaction_post_filename, 0, 1)
            if orig_filename and orig_post_url:
                update_reaction_collection(recent_posts_cache,
                                           base_dir, reaction_post_filename,
                                           reaction_url,
                                           reaction_actor,
                                           self.post_to_nickname,
                                           domain, debug, reaction_post_json,
                                           emoji_content)
                reaction_url = orig_post_url
                reaction_post_filename = orig_filename
            if debug:
                print('Updating emoji reaction for ' + reaction_post_filename)
            update_reaction_collection(recent_posts_cache,
                                       base_dir, reaction_post_filename,
                                       reaction_url,
                                       reaction_actor,
                                       self.post_to_nickname, domain,
                                       debug, None, emoji_content)
            if debug:
                print('Regenerating html post for changed ' +
                      'emoji reaction collection')
            # clear the icon from the cache so that it gets updated
            if reaction_post_json:
                cached_post_filename = \
                    get_cached_post_filename(base_dir, self.post_to_nickname,
                                             domain, reaction_post_json)
                if debug:
                    print('Reaction post json: ' + str(reaction_post_json))
                    print('Reaction post nickname: ' +
                          self.post_to_nickname + ' ' + domain)
                    print('Reaction post cache: ' + str(cached_post_filename))
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir,
                                             self.post_to_nickname, domain)
                show_repeats = not is_dm(reaction_post_json)
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        False,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        self.post_to_nickname, domain,
                                        self.server.port, reaction_post_json,
                                        None, True,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        False, True, False,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Emoji reaction post not found: ' +
                      reaction_post_filename)
        else:
            print('WARN: unable to locate file for emoji reaction post ' +
                  reaction_url)

        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + \
            '?page=' + str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_reaction_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie,
                               calling_domain)

    def _undo_reaction_button(self, calling_domain: str, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              proxy_type: str, cookie: str,
                              debug: str) -> None:
        """A button is pressed to undo emoji reaction
        """
        page_number = 1
        reaction_url = path.split('?unreact=')[1]
        if '?' in reaction_url:
            reaction_url = reaction_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        actor = path.split('?unreact=')[0]
        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number)
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        emoji_content_encoded = None
        if '?emojreact=' in path:
            emoji_content_encoded = path.split('?emojreact=')[1]
            if '?' in emoji_content_encoded:
                emoji_content_encoded = emoji_content_encoded.split('?')[0]
        if not emoji_content_encoded:
            print('WARN: no emoji reaction ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number) + timeline_bookmark
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        emoji_content = urllib.parse.unquote_plus(emoji_content_encoded)
        if not self._establish_session("undoReactionButton"):
            self._404()
            return
        undo_actor = \
            local_actor_url(http_prefix, self.post_to_nickname, domain_full)
        actor_reaction = path.split('?actor=')[1]
        if '?' in actor_reaction:
            actor_reaction = actor_reaction.split('?')[0]

        # if this is an announce then send the emoji reaction
        # to the original post
        orig_actor, orig_post_url, orig_filename = \
            get_original_post_from_announce_url(reaction_url, base_dir,
                                                self.post_to_nickname, domain)
        reaction_url2 = reaction_url
        reaction_post_filename = orig_filename
        if orig_actor and orig_post_url:
            actor_reaction = orig_actor
            reaction_url2 = orig_post_url
            reaction_post_filename = None

        undo_reaction_json = {
            "@context": "https://www.w3.org/ns/activitystreams",
            'type': 'Undo',
            'actor': undo_actor,
            'to': [actor_reaction],
            'object': {
                'type': 'EmojiReact',
                'actor': undo_actor,
                'to': [actor_reaction],
                'object': reaction_url2
            }
        }

        # send out the undo emoji reaction to followers
        self._post_to_outbox(undo_reaction_json,
                             self.server.project_version, None)

        # directly undo the emoji reaction within the post file
        if not reaction_post_filename:
            reaction_post_filename = \
                locate_post(base_dir, self.post_to_nickname, domain,
                            reaction_url)
        if reaction_post_filename:
            recent_posts_cache = self.server.recent_posts_cache
            reaction_post_json = load_json(reaction_post_filename, 0, 1)
            if orig_filename and orig_post_url:
                undo_reaction_collection_entry(recent_posts_cache,
                                               base_dir,
                                               reaction_post_filename,
                                               reaction_url,
                                               undo_actor, domain, debug,
                                               reaction_post_json,
                                               emoji_content)
                reaction_url = orig_post_url
                reaction_post_filename = orig_filename
            if debug:
                print('Removing emoji reaction for ' + reaction_post_filename)
            undo_reaction_collection_entry(recent_posts_cache,
                                           base_dir, reaction_post_filename,
                                           reaction_url,
                                           undo_actor, domain, debug,
                                           reaction_post_json, emoji_content)
            if debug:
                print('Regenerating html post for changed ' +
                      'emoji reaction collection')
            if reaction_post_json:
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir,
                                             self.post_to_nickname, domain)
                show_repeats = not is_dm(reaction_post_json)
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        False,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        self.post_to_nickname, domain,
                                        self.server.port, reaction_post_json,
                                        None, True,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        False, True, False,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Unreaction post not found: ' +
                      reaction_post_filename)

        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + \
            '?page=' + str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_undo_reaction_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie, calling_domain)

    def _reaction_picker(self, calling_domain: str, path: str,
                         base_dir: str, http_prefix: str,
                         domain: str, domain_full: str, port: int,
                         onion_domain: str, i2p_domain: str,
                         getreq_start_time,
                         proxy_type: str, cookie: str,
                         debug: str) -> None:
        """Press the emoji reaction picker icon at the bottom of the post
        """
        page_number = 1
        reaction_url = path.split('?selreact=')[1]
        if '?' in reaction_url:
            reaction_url = reaction_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        actor = path.split('?selreact=')[0]
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number) + timeline_bookmark
            self._redirect_headers(actor_path_str, cookie, calling_domain)
            return

        post_json_object = None
        reaction_post_filename = \
            locate_post(self.server.base_dir,
                        self.post_to_nickname, domain, reaction_url)
        if reaction_post_filename:
            post_json_object = load_json(reaction_post_filename)
        if not reaction_post_filename or not post_json_object:
            print('WARN: unable to locate reaction post ' + reaction_url)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number) + timeline_bookmark
            self._redirect_headers(actor_path_str, cookie, calling_domain)
            return

        msg = \
            html_emoji_reaction_picker(self.server.css_cache,
                                       self.server.recent_posts_cache,
                                       self.server.max_recent_posts,
                                       self.server.translate,
                                       self.server.base_dir,
                                       self.server.session,
                                       self.server.cached_webfingers,
                                       self.server.person_cache,
                                       self.post_to_nickname,
                                       domain, port, post_json_object,
                                       self.server.http_prefix,
                                       self.server.project_version,
                                       self.server.yt_replace_domain,
                                       self.server.twitter_replacement_domain,
                                       self.server.show_published_date_only,
                                       self.server.peertube_instances,
                                       self.server.allow_local_network_access,
                                       self.server.theme_name,
                                       self.server.system_language,
                                       self.server.max_like_count,
                                       self.server.signing_priv_key_pem,
                                       self.server.cw_lists,
                                       self.server.lists_enabled,
                                       timeline_str, page_number)
        msg = msg.encode('utf-8')
        msglen = len(msg)
        self._set_headers('text/html', msglen,
                          cookie, calling_domain, False)
        self._write(msg)
        fitness_performance(getreq_start_time,
                            self.server.fitness,
                            '_GET', '_reaction_picker',
                            self.server.debug)

    def _bookmark_button(self, calling_domain: str, path: str,
                         base_dir: str, http_prefix: str,
                         domain: str, domain_full: str, port: int,
                         onion_domain: str, i2p_domain: str,
                         getreq_start_time,
                         proxy_type: str, cookie: str,
                         debug: str) -> None:
        """Bookmark button was pressed
        """
        page_number = 1
        bookmark_url = path.split('?bookmark=')[1]
        if '?' in bookmark_url:
            bookmark_url = bookmark_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        actor = path.split('?bookmark=')[0]
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]

        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number)
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        if not self._establish_session("bookmarkButton"):
            self._404()
            return
        bookmark_actor = \
            local_actor_url(http_prefix, self.post_to_nickname, domain_full)
        cc_list = []
        bookmark_post(self.server.recent_posts_cache,
                      self.server.session,
                      base_dir,
                      self.server.federation_list,
                      self.post_to_nickname,
                      domain, port,
                      cc_list,
                      http_prefix,
                      bookmark_url, bookmark_actor, False,
                      self.server.send_threads,
                      self.server.postLog,
                      self.server.person_cache,
                      self.server.cached_webfingers,
                      self.server.debug,
                      self.server.project_version)
        # clear the icon from the cache so that it gets updated
        if self.server.iconsCache.get('bookmark.png'):
            del self.server.iconsCache['bookmark.png']
        bookmark_filename = \
            locate_post(base_dir, self.post_to_nickname, domain, bookmark_url)
        if bookmark_filename:
            print('Regenerating html post for changed bookmark')
            bookmark_post_json = load_json(bookmark_filename, 0, 1)
            if bookmark_post_json:
                cached_post_filename = \
                    get_cached_post_filename(base_dir, self.post_to_nickname,
                                             domain, bookmark_post_json)
                print('Bookmarked post json: ' + str(bookmark_post_json))
                print('Bookmarked post nickname: ' +
                      self.post_to_nickname + ' ' + domain)
                print('Bookmarked post cache: ' + str(cached_post_filename))
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir,
                                             self.post_to_nickname, domain)
                show_repeats = not is_dm(bookmark_post_json)
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        False,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        self.post_to_nickname, domain,
                                        self.server.port, bookmark_post_json,
                                        None, True,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        False, True, False,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Bookmarked post not found: ' + bookmark_filename)
        # self._post_to_outbox(bookmark_json,
        # self.server.project_version, None)
        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + \
            '?page=' + str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_bookmark_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie,
                               calling_domain)

    def _undo_bookmark_button(self, calling_domain: str, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str, port: int,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              proxy_type: str, cookie: str,
                              debug: str) -> None:
        """Button pressed to undo a bookmark
        """
        page_number = 1
        bookmark_url = path.split('?unbookmark=')[1]
        if '?' in bookmark_url:
            bookmark_url = bookmark_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        timeline_str = 'inbox'
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        actor = path.split('?unbookmark=')[0]
        self.post_to_nickname = get_nickname_from_actor(actor)
        if not self.post_to_nickname:
            print('WARN: unable to find nickname in ' + actor)
            actor_absolute = self._get_instance_url(calling_domain) + actor
            actor_path_str = \
                actor_absolute + '/' + timeline_str + \
                '?page=' + str(page_number)
            self._redirect_headers(actor_path_str, cookie,
                                   calling_domain)
            return
        if not self._establish_session("undo_bookmarkButton"):
            self._404()
            return
        undo_actor = \
            local_actor_url(http_prefix, self.post_to_nickname, domain_full)
        cc_list = []
        undo_bookmark_post(self.server.recent_posts_cache,
                           self.server.session,
                           base_dir,
                           self.server.federation_list,
                           self.post_to_nickname,
                           domain, port,
                           cc_list,
                           http_prefix,
                           bookmark_url, undo_actor, False,
                           self.server.send_threads,
                           self.server.postLog,
                           self.server.person_cache,
                           self.server.cached_webfingers,
                           debug,
                           self.server.project_version)
        # clear the icon from the cache so that it gets updated
        if self.server.iconsCache.get('bookmark_inactive.png'):
            del self.server.iconsCache['bookmark_inactive.png']
        # self._post_to_outbox(undo_bookmark_json,
        #                    self.server.project_version, None)
        bookmark_filename = \
            locate_post(base_dir, self.post_to_nickname, domain, bookmark_url)
        if bookmark_filename:
            print('Regenerating html post for changed unbookmark')
            bookmark_post_json = load_json(bookmark_filename, 0, 1)
            if bookmark_post_json:
                cached_post_filename = \
                    get_cached_post_filename(base_dir, self.post_to_nickname,
                                             domain, bookmark_post_json)
                print('Unbookmarked post json: ' + str(bookmark_post_json))
                print('Unbookmarked post nickname: ' +
                      self.post_to_nickname + ' ' + domain)
                print('Unbookmarked post cache: ' + str(cached_post_filename))
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir,
                                             self.post_to_nickname, domain)
                show_repeats = not is_dm(bookmark_post_json)
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        False,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        self.post_to_nickname, domain,
                                        self.server.port, bookmark_post_json,
                                        None, True,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        False, True, False,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Unbookmarked post not found: ' +
                      bookmark_filename)
        actor_absolute = self._get_instance_url(calling_domain) + actor
        actor_path_str = \
            actor_absolute + '/' + timeline_str + \
            '?page=' + str(page_number) + timeline_bookmark
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_undo_bookmark_button',
                            self.server.debug)
        self._redirect_headers(actor_path_str, cookie,
                               calling_domain)

    def _delete_button(self, calling_domain: str, path: str,
                       base_dir: str, http_prefix: str,
                       domain: str, domain_full: str, port: int,
                       onion_domain: str, i2p_domain: str,
                       getreq_start_time,
                       proxy_type: str, cookie: str,
                       debug: str) -> None:
        """Delete button is pressed on a post
        """
        if not cookie:
            print('ERROR: no cookie given when deleting ' + path)
            self._400()
            return
        page_number = 1
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        delete_url = path.split('?delete=')[1]
        if '?' in delete_url:
            delete_url = delete_url.split('?')[0]
        timeline_str = self.server.default_timeline
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        users_path = path.split('?delete=')[0]
        actor = \
            http_prefix + '://' + domain_full + users_path
        if self.server.allow_deletion or \
           delete_url.startswith(actor):
            if self.server.debug:
                print('DEBUG: delete_url=' + delete_url)
                print('DEBUG: actor=' + actor)
            if actor not in delete_url:
                # You can only delete your own posts
                if calling_domain.endswith('.onion') and onion_domain:
                    actor = 'http://' + onion_domain + users_path
                elif calling_domain.endswith('.i2p') and i2p_domain:
                    actor = 'http://' + i2p_domain + users_path
                self._redirect_headers(actor + '/' + timeline_str,
                                       cookie, calling_domain)
                return
            self.post_to_nickname = get_nickname_from_actor(actor)
            if not self.post_to_nickname:
                print('WARN: unable to find nickname in ' + actor)
                if calling_domain.endswith('.onion') and onion_domain:
                    actor = 'http://' + onion_domain + users_path
                elif calling_domain.endswith('.i2p') and i2p_domain:
                    actor = 'http://' + i2p_domain + users_path
                self._redirect_headers(actor + '/' + timeline_str,
                                       cookie, calling_domain)
                return
            if not self._establish_session("deleteButton"):
                self._404()
                return

            delete_str = \
                html_confirm_delete(self.server.css_cache,
                                    self.server.recent_posts_cache,
                                    self.server.max_recent_posts,
                                    self.server.translate, page_number,
                                    self.server.session, base_dir,
                                    delete_url, http_prefix,
                                    self.server.project_version,
                                    self.server.cached_webfingers,
                                    self.server.person_cache, calling_domain,
                                    self.server.yt_replace_domain,
                                    self.server.twitter_replacement_domain,
                                    self.server.show_published_date_only,
                                    self.server.peertube_instances,
                                    self.server.allow_local_network_access,
                                    self.server.theme_name,
                                    self.server.system_language,
                                    self.server.max_like_count,
                                    self.server.signing_priv_key_pem,
                                    self.server.cw_lists,
                                    self.server.lists_enabled)
            if delete_str:
                delete_str_len = len(delete_str)
                self._set_headers('text/html', delete_str_len,
                                  cookie, calling_domain, False)
                self._write(delete_str.encode('utf-8'))
                self.server.getreq_busy = False
                return
        if calling_domain.endswith('.onion') and onion_domain:
            actor = 'http://' + onion_domain + users_path
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            actor = 'http://' + i2p_domain + users_path
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_delete_button',
                            self.server.debug)
        self._redirect_headers(actor + '/' + timeline_str,
                               cookie, calling_domain)

    def _mute_button(self, calling_domain: str, path: str,
                     base_dir: str, http_prefix: str,
                     domain: str, domain_full: str, port: int,
                     onion_domain: str, i2p_domain: str,
                     getreq_start_time,
                     proxy_type: str, cookie: str,
                     debug: str):
        """Mute button is pressed
        """
        mute_url = path.split('?mute=')[1]
        if '?' in mute_url:
            mute_url = mute_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        timeline_str = self.server.default_timeline
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        page_number = 1
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        actor = \
            http_prefix + '://' + domain_full + path.split('?mute=')[0]
        nickname = get_nickname_from_actor(actor)
        mute_post(base_dir, nickname, domain, port,
                  http_prefix, mute_url,
                  self.server.recent_posts_cache, debug)
        mute_filename = \
            locate_post(base_dir, nickname, domain, mute_url)
        if mute_filename:
            print('mute_post: Regenerating html post for changed mute status')
            mute_post_json = load_json(mute_filename, 0, 1)
            if mute_post_json:
                cached_post_filename = \
                    get_cached_post_filename(base_dir, nickname,
                                             domain, mute_post_json)
                print('mute_post: Muted post json: ' + str(mute_post_json))
                print('mute_post: Muted post nickname: ' +
                      nickname + ' ' + domain)
                print('mute_post: Muted post cache: ' +
                      str(cached_post_filename))
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir,
                                             nickname, domain)
                show_repeats = not is_dm(mute_post_json)
                show_public_only = False
                store_to_cache = True
                use_cache_only = False
                allow_downloads = False
                show_avatar_options = True
                avatar_url = None
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        allow_downloads,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        nickname, domain,
                                        self.server.port, mute_post_json,
                                        avatar_url, show_avatar_options,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        show_public_only, store_to_cache,
                                        use_cache_only,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Muted post not found: ' + mute_filename)

        if calling_domain.endswith('.onion') and onion_domain:
            actor = \
                'http://' + onion_domain + \
                path.split('?mute=')[0]
        elif (calling_domain.endswith('.i2p') and i2p_domain):
            actor = \
                'http://' + i2p_domain + \
                path.split('?mute=')[0]
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_mute_button', self.server.debug)
        self._redirect_headers(actor + '/' +
                               timeline_str + timeline_bookmark,
                               cookie, calling_domain)

    def _undo_mute_button(self, calling_domain: str, path: str,
                          base_dir: str, http_prefix: str,
                          domain: str, domain_full: str, port: int,
                          onion_domain: str, i2p_domain: str,
                          getreq_start_time,
                          proxy_type: str, cookie: str,
                          debug: str):
        """Undo mute button is pressed
        """
        mute_url = path.split('?unmute=')[1]
        if '?' in mute_url:
            mute_url = mute_url.split('?')[0]
        timeline_bookmark = ''
        if '?bm=' in path:
            timeline_bookmark = path.split('?bm=')[1]
            if '?' in timeline_bookmark:
                timeline_bookmark = timeline_bookmark.split('?')[0]
            timeline_bookmark = '#' + timeline_bookmark
        timeline_str = self.server.default_timeline
        if '?tl=' in path:
            timeline_str = path.split('?tl=')[1]
            if '?' in timeline_str:
                timeline_str = timeline_str.split('?')[0]
        page_number = 1
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
        actor = \
            http_prefix + '://' + domain_full + path.split('?unmute=')[0]
        nickname = get_nickname_from_actor(actor)
        unmute_post(base_dir, nickname, domain, port,
                    http_prefix, mute_url,
                    self.server.recent_posts_cache, debug)
        mute_filename = \
            locate_post(base_dir, nickname, domain, mute_url)
        if mute_filename:
            print('unmute_post: ' +
                  'Regenerating html post for changed unmute status')
            mute_post_json = load_json(mute_filename, 0, 1)
            if mute_post_json:
                cached_post_filename = \
                    get_cached_post_filename(base_dir, nickname,
                                             domain, mute_post_json)
                print('unmute_post: Unmuted post json: ' + str(mute_post_json))
                print('unmute_post: Unmuted post nickname: ' +
                      nickname + ' ' + domain)
                print('unmute_post: Unmuted post cache: ' +
                      str(cached_post_filename))
                show_individual_post_icons = True
                manually_approve_followers = \
                    follower_approval_active(base_dir, nickname, domain)
                show_repeats = not is_dm(mute_post_json)
                show_public_only = False
                store_to_cache = True
                use_cache_only = False
                allow_downloads = False
                show_avatar_options = True
                avatar_url = None
                individual_post_as_html(self.server.signing_priv_key_pem,
                                        allow_downloads,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, base_dir,
                                        self.server.session,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        nickname, domain,
                                        self.server.port, mute_post_json,
                                        avatar_url, show_avatar_options,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        timeline_str,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.theme_name,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        show_repeats,
                                        show_individual_post_icons,
                                        manually_approve_followers,
                                        show_public_only, store_to_cache,
                                        use_cache_only,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
            else:
                print('WARN: Unmuted post not found: ' + mute_filename)
        if calling_domain.endswith('.onion') and onion_domain:
            actor = \
                'http://' + onion_domain + path.split('?unmute=')[0]
        elif calling_domain.endswith('.i2p') and i2p_domain:
            actor = \
                'http://' + i2p_domain + path.split('?unmute=')[0]
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_undo_mute_button', self.server.debug)
        self._redirect_headers(actor + '/' + timeline_str +
                               timeline_bookmark,
                               cookie, calling_domain)

    def _show_replies_to_post(self, authorized: bool,
                              calling_domain: str, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str, port: int,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              proxy_type: str, cookie: str,
                              debug: str) -> bool:
        """Shows the replies to a post
        """
        if not ('/statuses/' in path and '/users/' in path):
            return False

        named_status = path.split('/users/')[1]
        if '/' not in named_status:
            return False

        post_sections = named_status.split('/')
        if len(post_sections) < 4:
            return False

        if not post_sections[3].startswith('replies'):
            return False
        nickname = post_sections[0]
        status_number = post_sections[2]
        if not (len(status_number) > 10 and status_number.isdigit()):
            return False

        boxname = 'outbox'
        # get the replies file
        post_dir = \
            acct_dir(base_dir, nickname, domain) + '/' + boxname
        post_replies_filename = \
            post_dir + '/' + \
            http_prefix + ':##' + domain_full + '#users#' + \
            nickname + '#statuses#' + status_number + '.replies'
        if not os.path.isfile(post_replies_filename):
            # There are no replies,
            # so show empty collection
            context_str = \
                'https://www.w3.org/ns/activitystreams'

            first_str = \
                local_actor_url(http_prefix, nickname, domain_full) + \
                '/statuses/' + status_number + '/replies?page=true'

            id_str = \
                local_actor_url(http_prefix, nickname, domain_full) + \
                '/statuses/' + status_number + '/replies'

            last_str = \
                local_actor_url(http_prefix, nickname, domain_full) + \
                '/statuses/' + status_number + '/replies?page=true'

            replies_json = {
                '@context': context_str,
                'first': first_str,
                'id': id_str,
                'last': last_str,
                'totalItems': 0,
                'type': 'OrderedCollection'
            }

            if self._request_http():
                if not self._establish_session("showRepliesToPost"):
                    self._404()
                    return True
                recent_posts_cache = self.server.recent_posts_cache
                max_recent_posts = self.server.max_recent_posts
                translate = self.server.translate
                session = self.server.session
                cached_webfingers = self.server.cached_webfingers
                person_cache = self.server.person_cache
                project_version = self.server.project_version
                yt_domain = self.server.yt_replace_domain
                twitter_replacement_domain = \
                    self.server.twitter_replacement_domain
                peertube_instances = self.server.peertube_instances
                msg = \
                    html_post_replies(self.server.css_cache,
                                      recent_posts_cache,
                                      max_recent_posts,
                                      translate,
                                      base_dir,
                                      session,
                                      cached_webfingers,
                                      person_cache,
                                      nickname,
                                      domain,
                                      port,
                                      replies_json,
                                      http_prefix,
                                      project_version,
                                      yt_domain,
                                      twitter_replacement_domain,
                                      self.server.show_published_date_only,
                                      peertube_instances,
                                      self.server.allow_local_network_access,
                                      self.server.theme_name,
                                      self.server.system_language,
                                      self.server.max_like_count,
                                      self.server.signing_priv_key_pem,
                                      self.server.cw_lists,
                                      self.server.lists_enabled)
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_show_replies_to_post',
                                    self.server.debug)
            else:
                if self._secure_mode():
                    msg = json.dumps(replies_json, ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    protocol_str = 'application/json'
                    msglen = len(msg)
                    self._set_headers(protocol_str, msglen, None,
                                      calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', '_show_replies_to_post json',
                                        self.server.debug)
                else:
                    self._404()
            return True
        else:
            # replies exist. Itterate through the
            # text file containing message ids
            context_str = 'https://www.w3.org/ns/activitystreams'

            id_str = \
                local_actor_url(http_prefix, nickname, domain_full) + \
                '/statuses/' + status_number + '?page=true'

            part_of_str = \
                local_actor_url(http_prefix, nickname, domain_full) + \
                '/statuses/' + status_number

            replies_json = {
                '@context': context_str,
                'id': id_str,
                'orderedItems': [
                ],
                'partOf': part_of_str,
                'type': 'OrderedCollectionPage'
            }

            # populate the items list with replies
            populate_replies_json(base_dir, nickname, domain,
                                  post_replies_filename,
                                  authorized, replies_json)

            # send the replies json
            if self._request_http():
                if not self._establish_session("showRepliesToPost2"):
                    self._404()
                    return True
                recent_posts_cache = self.server.recent_posts_cache
                max_recent_posts = self.server.max_recent_posts
                translate = self.server.translate
                session = self.server.session
                cached_webfingers = self.server.cached_webfingers
                person_cache = self.server.person_cache
                project_version = self.server.project_version
                yt_domain = self.server.yt_replace_domain
                twitter_replacement_domain = \
                    self.server.twitter_replacement_domain
                peertube_instances = self.server.peertube_instances
                msg = \
                    html_post_replies(self.server.css_cache,
                                      recent_posts_cache,
                                      max_recent_posts,
                                      translate,
                                      base_dir,
                                      session,
                                      cached_webfingers,
                                      person_cache,
                                      nickname,
                                      domain,
                                      port,
                                      replies_json,
                                      http_prefix,
                                      project_version,
                                      yt_domain,
                                      twitter_replacement_domain,
                                      self.server.show_published_date_only,
                                      peertube_instances,
                                      self.server.allow_local_network_access,
                                      self.server.theme_name,
                                      self.server.system_language,
                                      self.server.max_like_count,
                                      self.server.signing_priv_key_pem,
                                      self.server.cw_lists,
                                      self.server.lists_enabled)
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_show_replies_to_post',
                                    self.server.debug)
            else:
                if self._secure_mode():
                    msg = json.dumps(replies_json,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    protocol_str = 'application/json'
                    msglen = len(msg)
                    self._set_headers(protocol_str, msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', '_show_replies_to_post json',
                                        self.server.debug)
                else:
                    self._404()
            return True
        return False

    def _show_roles(self, authorized: bool,
                    calling_domain: str, path: str,
                    base_dir: str, http_prefix: str,
                    domain: str, domain_full: str, port: int,
                    onion_domain: str, i2p_domain: str,
                    getreq_start_time,
                    proxy_type: str, cookie: str,
                    debug: str) -> bool:
        """Show roles within profile screen
        """
        named_status = path.split('/users/')[1]
        if '/' not in named_status:
            return False

        post_sections = named_status.split('/')
        nickname = post_sections[0]
        actor_filename = acct_dir(base_dir, nickname, domain) + '.json'
        if not os.path.isfile(actor_filename):
            return False

        actor_json = load_json(actor_filename)
        if not actor_json:
            return False

        if actor_json.get('hasOccupation'):
            if self._request_http():
                get_person = \
                    person_lookup(domain, path.replace('/roles', ''),
                                  base_dir)
                if get_person:
                    default_timeline = \
                        self.server.default_timeline
                    recent_posts_cache = \
                        self.server.recent_posts_cache
                    cached_webfingers = \
                        self.server.cached_webfingers
                    yt_replace_domain = \
                        self.server.yt_replace_domain
                    twitter_replacement_domain = \
                        self.server.twitter_replacement_domain
                    icons_as_buttons = \
                        self.server.icons_as_buttons

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = self.server.key_shortcuts[nickname]

                    roles_list = get_actor_roles_list(actor_json)
                    city = \
                        get_spoofed_city(self.server.city,
                                         base_dir, nickname, domain)
                    shared_items_federated_domains = \
                        self.server.shared_items_federated_domains
                    msg = \
                        html_profile(self.server.signing_priv_key_pem,
                                     self.server.rss_icon_at_top,
                                     self.server.css_cache,
                                     icons_as_buttons,
                                     default_timeline,
                                     recent_posts_cache,
                                     self.server.max_recent_posts,
                                     self.server.translate,
                                     self.server.project_version,
                                     base_dir, http_prefix, True,
                                     get_person, 'roles',
                                     self.server.session,
                                     cached_webfingers,
                                     self.server.person_cache,
                                     yt_replace_domain,
                                     twitter_replacement_domain,
                                     self.server.show_published_date_only,
                                     self.server.newswire,
                                     self.server.theme_name,
                                     self.server.dormant_months,
                                     self.server.peertube_instances,
                                     self.server.allow_local_network_access,
                                     self.server.text_mode_banner,
                                     self.server.debug,
                                     access_keys, city,
                                     self.server.system_language,
                                     self.server.max_like_count,
                                     shared_items_federated_domains,
                                     roles_list,
                                     None, None, self.server.cw_lists,
                                     self.server.lists_enabled,
                                     self.server.content_license_url)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', '_show_roles',
                                        self.server.debug)
            else:
                if self._secure_mode():
                    roles_list = get_actor_roles_list(actor_json)
                    msg = json.dumps(roles_list,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', '_show_roles json',
                                        self.server.debug)
                else:
                    self._404()
            return True
        return False

    def _show_skills(self, authorized: bool,
                     calling_domain: str, path: str,
                     base_dir: str, http_prefix: str,
                     domain: str, domain_full: str, port: int,
                     onion_domain: str, i2p_domain: str,
                     getreq_start_time,
                     proxy_type: str, cookie: str,
                     debug: str) -> bool:
        """Show skills on the profile screen
        """
        named_status = path.split('/users/')[1]
        if '/' in named_status:
            post_sections = named_status.split('/')
            nickname = post_sections[0]
            actor_filename = acct_dir(base_dir, nickname, domain) + '.json'
            if os.path.isfile(actor_filename):
                actor_json = load_json(actor_filename)
                if actor_json:
                    if no_of_actor_skills(actor_json) > 0:
                        if self._request_http():
                            get_person = \
                                person_lookup(domain,
                                              path.replace('/skills', ''),
                                              base_dir)
                            if get_person:
                                default_timeline =  \
                                    self.server.default_timeline
                                recent_posts_cache = \
                                    self.server.recent_posts_cache
                                cached_webfingers = \
                                    self.server.cached_webfingers
                                yt_replace_domain = \
                                    self.server.yt_replace_domain
                                twitter_replacement_domain = \
                                    self.server.twitter_replacement_domain
                                show_published_date_only = \
                                    self.server.show_published_date_only
                                icons_as_buttons = \
                                    self.server.icons_as_buttons
                                allow_local_network_access = \
                                    self.server.allow_local_network_access
                                access_keys = self.server.access_keys
                                if self.server.key_shortcuts.get(nickname):
                                    access_keys = \
                                        self.server.key_shortcuts[nickname]
                                actor_skills_list = \
                                    get_occupation_skills(actor_json)
                                skills = \
                                    get_skills_from_list(actor_skills_list)
                                city = get_spoofed_city(self.server.city,
                                                        base_dir,
                                                        nickname, domain)
                                shared_items_fed_domains = \
                                    self.server.shared_items_federated_domains
                                signing_priv_key_pem = \
                                    self.server.signing_priv_key_pem
                                content_license_url = \
                                    self.server.content_license_url
                                peertube_instances = \
                                    self.server.peertube_instances
                                msg = \
                                    html_profile(signing_priv_key_pem,
                                                 self.server.rss_icon_at_top,
                                                 self.server.css_cache,
                                                 icons_as_buttons,
                                                 default_timeline,
                                                 recent_posts_cache,
                                                 self.server.max_recent_posts,
                                                 self.server.translate,
                                                 self.server.project_version,
                                                 base_dir, http_prefix, True,
                                                 get_person, 'skills',
                                                 self.server.session,
                                                 cached_webfingers,
                                                 self.server.person_cache,
                                                 yt_replace_domain,
                                                 twitter_replacement_domain,
                                                 show_published_date_only,
                                                 self.server.newswire,
                                                 self.server.theme_name,
                                                 self.server.dormant_months,
                                                 peertube_instances,
                                                 allow_local_network_access,
                                                 self.server.text_mode_banner,
                                                 self.server.debug,
                                                 access_keys, city,
                                                 self.server.system_language,
                                                 self.server.max_like_count,
                                                 shared_items_fed_domains,
                                                 skills,
                                                 None, None,
                                                 self.server.cw_lists,
                                                 self.server.lists_enabled,
                                                 content_license_url)
                                msg = msg.encode('utf-8')
                                msglen = len(msg)
                                self._set_headers('text/html', msglen,
                                                  cookie, calling_domain,
                                                  False)
                                self._write(msg)
                                fitness_performance(getreq_start_time,
                                                    self.server.fitness,
                                                    '_GET', '_show_skills',
                                                    self.server.debug)
                        else:
                            if self._secure_mode():
                                actor_skills_list = \
                                    get_occupation_skills(actor_json)
                                skills = \
                                    get_skills_from_list(actor_skills_list)
                                msg = json.dumps(skills,
                                                 ensure_ascii=False)
                                msg = msg.encode('utf-8')
                                msglen = len(msg)
                                self._set_headers('application/json',
                                                  msglen, None,
                                                  calling_domain, False)
                                self._write(msg)
                                fitness_performance(getreq_start_time,
                                                    self.server.fitness,
                                                    '_GET',
                                                    '_show_skills json',
                                                    self.server.debug)
                            else:
                                self._404()
                        return True
        actor = path.replace('/skills', '')
        actor_absolute = self._get_instance_url(calling_domain) + actor
        self._redirect_headers(actor_absolute, cookie, calling_domain)
        return True

    def _show_individual_at_post(self, authorized: bool,
                                 calling_domain: str, path: str,
                                 base_dir: str, http_prefix: str,
                                 domain: str, domain_full: str, port: int,
                                 onion_domain: str, i2p_domain: str,
                                 getreq_start_time,
                                 proxy_type: str, cookie: str,
                                 debug: str) -> bool:
        """get an individual post from the path /@nickname/statusnumber
        """
        if '/@' not in path:
            return False

        liked_by = None
        if '?likedBy=' in path:
            liked_by = path.split('?likedBy=')[1].strip()
            if '?' in liked_by:
                liked_by = liked_by.split('?')[0]
            path = path.split('?likedBy=')[0]

        react_by = None
        react_emoji = None
        if '?reactBy=' in path:
            react_by = path.split('?reactBy=')[1].strip()
            if ';' in react_by:
                react_by = react_by.split(';')[0]
            if ';emoj=' in path:
                react_emoji = path.split(';emoj=')[1].strip()
                if ';' in react_emoji:
                    react_emoji = react_emoji.split(';')[0]
            path = path.split('?reactBy=')[0]

        named_status = path.split('/@')[1]
        if '/' not in named_status:
            # show actor
            nickname = named_status
            return False

        post_sections = named_status.split('/')
        if len(post_sections) != 2:
            return False
        nickname = post_sections[0]
        status_number = post_sections[1]
        if len(status_number) <= 10 or not status_number.isdigit():
            return False

        post_filename = \
            acct_dir(base_dir, nickname, domain) + '/outbox/' + \
            http_prefix + ':##' + domain_full + '#users#' + nickname + \
            '#statuses#' + status_number + '.json'

        include_create_wrapper = False
        if post_sections[-1] == 'activity':
            include_create_wrapper = True

        result = self._show_post_from_file(post_filename, liked_by,
                                           react_by, react_emoji,
                                           authorized, calling_domain, path,
                                           base_dir, http_prefix, nickname,
                                           domain, domain_full, port,
                                           onion_domain, i2p_domain,
                                           getreq_start_time,
                                           proxy_type, cookie, debug,
                                           include_create_wrapper)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_show_individual_at_post',
                            self.server.debug)
        return result

    def _show_post_from_file(self, post_filename: str, liked_by: str,
                             react_by: str, react_emoji: str,
                             authorized: bool,
                             calling_domain: str, path: str,
                             base_dir: str, http_prefix: str, nickname: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time,
                             proxy_type: str, cookie: str,
                             debug: str, include_create_wrapper: bool) -> bool:
        """Shows an individual post from its filename
        """
        if not os.path.isfile(post_filename):
            self._404()
            self.server.getreq_busy = False
            return True

        post_json_object = load_json(post_filename)
        if not post_json_object:
            self.send_response(429)
            self.end_headers()
            self.server.getreq_busy = False
            return True

        # Only authorized viewers get to see likes on posts
        # Otherwize marketers could gain more social graph info
        if not authorized:
            pjo = post_json_object
            if not is_public_post(pjo):
                self._404()
                self.server.getreq_busy = False
                return True
            remove_post_interactions(pjo, True)
        if self._request_http():
            msg = \
                html_individual_post(self.server.css_cache,
                                     self.server.recent_posts_cache,
                                     self.server.max_recent_posts,
                                     self.server.translate,
                                     base_dir,
                                     self.server.session,
                                     self.server.cached_webfingers,
                                     self.server.person_cache,
                                     nickname, domain, port,
                                     authorized,
                                     post_json_object,
                                     http_prefix,
                                     self.server.project_version,
                                     liked_by, react_by, react_emoji,
                                     self.server.yt_replace_domain,
                                     self.server.twitter_replacement_domain,
                                     self.server.show_published_date_only,
                                     self.server.peertube_instances,
                                     self.server.allow_local_network_access,
                                     self.server.theme_name,
                                     self.server.system_language,
                                     self.server.max_like_count,
                                     self.server.signing_priv_key_pem,
                                     self.server.cw_lists,
                                     self.server.lists_enabled)
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', '_show_post_from_file',
                                self.server.debug)
        else:
            if self._secure_mode():
                if not include_create_wrapper and \
                   post_json_object['type'] == 'Create' and \
                   has_object_dict(post_json_object):
                    unwrapped_json = post_json_object['object']
                    unwrapped_json['@context'] = \
                        get_individual_post_context()
                    msg = json.dumps(unwrapped_json,
                                     ensure_ascii=False)
                else:
                    msg = json.dumps(post_json_object,
                                     ensure_ascii=False)
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._set_headers('application/json',
                                  msglen,
                                  None, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', '_show_post_from_file json',
                                    self.server.debug)
            else:
                self._404()
        self.server.getreq_busy = False
        return True

    def _show_individual_post(self, authorized: bool,
                              calling_domain: str, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str, port: int,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              proxy_type: str, cookie: str,
                              debug: str) -> bool:
        """Shows an individual post
        """
        liked_by = None
        if '?likedBy=' in path:
            liked_by = path.split('?likedBy=')[1].strip()
            if '?' in liked_by:
                liked_by = liked_by.split('?')[0]
            path = path.split('?likedBy=')[0]

        react_by = None
        react_emoji = None
        if '?reactBy=' in path:
            react_by = path.split('?reactBy=')[1].strip()
            if ';' in react_by:
                react_by = react_by.split(';')[0]
            if ';emoj=' in path:
                react_emoji = path.split(';emoj=')[1].strip()
                if ';' in react_emoji:
                    react_emoji = react_emoji.split(';')[0]
            path = path.split('?reactBy=')[0]

        named_status = path.split('/users/')[1]
        if '/' not in named_status:
            return False
        post_sections = named_status.split('/')
        if len(post_sections) < 3:
            return False
        nickname = post_sections[0]
        status_number = post_sections[2]
        if len(status_number) <= 10 or (not status_number.isdigit()):
            return False

        post_filename = \
            acct_dir(base_dir, nickname, domain) + '/outbox/' + \
            http_prefix + ':##' + domain_full + '#users#' + nickname + \
            '#statuses#' + status_number + '.json'

        include_create_wrapper = False
        if post_sections[-1] == 'activity':
            include_create_wrapper = True

        result = self._show_post_from_file(post_filename, liked_by,
                                           react_by, react_emoji,
                                           authorized, calling_domain, path,
                                           base_dir, http_prefix, nickname,
                                           domain, domain_full, port,
                                           onion_domain, i2p_domain,
                                           getreq_start_time,
                                           proxy_type, cookie, debug,
                                           include_create_wrapper)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_show_individual_post',
                            self.server.debug)
        return result

    def _show_notify_post(self, authorized: bool,
                          calling_domain: str, path: str,
                          base_dir: str, http_prefix: str,
                          domain: str, domain_full: str, port: int,
                          onion_domain: str, i2p_domain: str,
                          getreq_start_time,
                          proxy_type: str, cookie: str,
                          debug: str) -> bool:
        """Shows an individual post from an account which you are following
        and where you have the notify checkbox set on person options
        """
        liked_by = None
        react_by = None
        react_emoji = None
        post_id = path.split('?notifypost=')[1].strip()
        post_id = post_id.replace('-', '/')
        path = path.split('?notifypost=')[0]
        nickname = path.split('/users/')[1]
        if '/' in nickname:
            return False
        replies = False

        post_filename = locate_post(base_dir, nickname, domain,
                                    post_id, replies)
        if not post_filename:
            return False

        include_create_wrapper = False
        if path.endswith('/activity'):
            include_create_wrapper = True

        result = self._show_post_from_file(post_filename, liked_by,
                                           react_by, react_emoji,
                                           authorized, calling_domain, path,
                                           base_dir, http_prefix, nickname,
                                           domain, domain_full, port,
                                           onion_domain, i2p_domain,
                                           getreq_start_time,
                                           proxy_type, cookie, debug,
                                           include_create_wrapper)
        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_show_notify_post',
                            self.server.debug)
        return result

    def _show_inbox(self, authorized: bool,
                    calling_domain: str, path: str,
                    base_dir: str, http_prefix: str,
                    domain: str, domain_full: str, port: int,
                    onion_domain: str, i2p_domain: str,
                    getreq_start_time,
                    proxy_type: str, cookie: str,
                    debug: str,
                    recent_posts_cache: {}, session,
                    default_timeline: str,
                    max_recent_posts: int,
                    translate: {},
                    cached_webfingers: {},
                    person_cache: {},
                    allow_deletion: bool,
                    project_version: str,
                    yt_replace_domain: str,
                    twitter_replacement_domain: str) -> bool:
        """Shows the inbox timeline
        """
        if '/users/' in path:
            if authorized:
                inbox_feed = \
                    person_box_json(recent_posts_cache,
                                    session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_FEED, 'inbox',
                                    authorized,
                                    0,
                                    self.server.positive_voting,
                                    self.server.voting_time_mins)
                if inbox_feed:
                    if getreq_start_time:
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', '_show_inbox',
                                            self.server.debug)
                    if self._request_http():
                        nickname = path.replace('/users/', '')
                        nickname = nickname.replace('/inbox', '')
                        page_number = 1
                        if '?page=' in nickname:
                            page_number = nickname.split('?page=')[1]
                            nickname = nickname.split('?page=')[0]
                            if page_number.isdigit():
                                page_number = int(page_number)
                            else:
                                page_number = 1
                        if 'page=' not in path:
                            # if no page was specified then show the first
                            inbox_feed = \
                                person_box_json(recent_posts_cache,
                                                session,
                                                base_dir,
                                                domain,
                                                port,
                                                path + '?page=1',
                                                http_prefix,
                                                MAX_POSTS_IN_FEED, 'inbox',
                                                authorized,
                                                0,
                                                self.server.positive_voting,
                                                self.server.voting_time_mins)
                            if getreq_start_time:
                                fitness_performance(getreq_start_time,
                                                    self.server.fitness,
                                                    '_GET', '_show_inbox2',
                                                    self.server.debug)
                        full_width_tl_button_header = \
                            self.server.full_width_tl_button_header
                        minimal_nick = is_minimal(base_dir, domain, nickname)

                        access_keys = self.server.access_keys
                        if self.server.key_shortcuts.get(nickname):
                            access_keys = \
                                self.server.key_shortcuts[nickname]
                        shared_items_federated_domains = \
                            self.server.shared_items_federated_domains
                        allow_local_network_access = \
                            self.server.allow_local_network_access
                        msg = html_inbox(self.server.css_cache,
                                         default_timeline,
                                         recent_posts_cache,
                                         max_recent_posts,
                                         translate,
                                         page_number, MAX_POSTS_IN_FEED,
                                         session,
                                         base_dir,
                                         cached_webfingers,
                                         person_cache,
                                         nickname,
                                         domain,
                                         port,
                                         inbox_feed,
                                         allow_deletion,
                                         http_prefix,
                                         project_version,
                                         minimal_nick,
                                         yt_replace_domain,
                                         twitter_replacement_domain,
                                         self.server.show_published_date_only,
                                         self.server.newswire,
                                         self.server.positive_voting,
                                         self.server.show_publish_as_icon,
                                         full_width_tl_button_header,
                                         self.server.icons_as_buttons,
                                         self.server.rss_icon_at_top,
                                         self.server.publish_button_at_top,
                                         authorized,
                                         self.server.theme_name,
                                         self.server.peertube_instances,
                                         allow_local_network_access,
                                         self.server.text_mode_banner,
                                         access_keys,
                                         self.server.system_language,
                                         self.server.max_like_count,
                                         shared_items_federated_domains,
                                         self.server.signing_priv_key_pem,
                                         self.server.cw_lists,
                                         self.server.lists_enabled)
                        if getreq_start_time:
                            fitness_performance(getreq_start_time,
                                                self.server.fitness,
                                                '_GET', '_show_inbox3',
                                                self.server.debug)
                        if msg:
                            msg = msg.encode('utf-8')
                            msglen = len(msg)
                            self._set_headers('text/html', msglen,
                                              cookie, calling_domain, False)
                            self._write(msg)

                        if getreq_start_time:
                            fitness_performance(getreq_start_time,
                                                self.server.fitness,
                                                '_GET', '_show_inbox4',
                                                self.server.debug)
                    else:
                        # don't need authorized fetch here because
                        # there is already the authorization check
                        msg = json.dumps(inbox_feed, ensure_ascii=False)
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('application/json', msglen,
                                          None, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', '_show_inbox5',
                                            self.server.debug)
                    return True
            else:
                if debug:
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/inbox', '')
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if path != '/inbox':
            # not the shared inbox
            if debug:
                print('DEBUG: GET access to inbox is unauthorized')
            self.send_response(405)
            self.end_headers()
            return True
        return False

    def _show_d_ms(self, authorized: bool,
                   calling_domain: str, path: str,
                   base_dir: str, http_prefix: str,
                   domain: str, domain_full: str, port: int,
                   onion_domain: str, i2p_domain: str,
                   getreq_start_time,
                   proxy_type: str, cookie: str,
                   debug: str) -> bool:
        """Shows the DMs timeline
        """
        if '/users/' in path:
            if authorized:
                inbox_dm_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_FEED, 'dm',
                                    authorized,
                                    0, self.server.positive_voting,
                                    self.server.voting_time_mins)
                if inbox_dm_feed:
                    if self._request_http():
                        nickname = path.replace('/users/', '')
                        nickname = nickname.replace('/dm', '')
                        page_number = 1
                        if '?page=' in nickname:
                            page_number = nickname.split('?page=')[1]
                            nickname = nickname.split('?page=')[0]
                            if page_number.isdigit():
                                page_number = int(page_number)
                            else:
                                page_number = 1
                        if 'page=' not in path:
                            # if no page was specified then show the first
                            inbox_dm_feed = \
                                person_box_json(self.server.recent_posts_cache,
                                                self.server.session,
                                                base_dir,
                                                domain,
                                                port,
                                                path + '?page=1',
                                                http_prefix,
                                                MAX_POSTS_IN_FEED, 'dm',
                                                authorized,
                                                0,
                                                self.server.positive_voting,
                                                self.server.voting_time_mins)
                        full_width_tl_button_header = \
                            self.server.full_width_tl_button_header
                        minimal_nick = is_minimal(base_dir, domain, nickname)

                        access_keys = self.server.access_keys
                        if self.server.key_shortcuts.get(nickname):
                            access_keys = \
                                self.server.key_shortcuts[nickname]

                        shared_items_federated_domains = \
                            self.server.shared_items_federated_domains
                        allow_local_network_access = \
                            self.server.allow_local_network_access
                        twitter_replacement_domain = \
                            self.server.twitter_replacement_domain
                        show_published_date_only = \
                            self.server.show_published_date_only
                        msg = \
                            html_inbox_dms(self.server.css_cache,
                                           self.server.default_timeline,
                                           self.server.recent_posts_cache,
                                           self.server.max_recent_posts,
                                           self.server.translate,
                                           page_number, MAX_POSTS_IN_FEED,
                                           self.server.session,
                                           base_dir,
                                           self.server.cached_webfingers,
                                           self.server.person_cache,
                                           nickname,
                                           domain,
                                           port,
                                           inbox_dm_feed,
                                           self.server.allow_deletion,
                                           http_prefix,
                                           self.server.project_version,
                                           minimal_nick,
                                           self.server.yt_replace_domain,
                                           twitter_replacement_domain,
                                           show_published_date_only,
                                           self.server.newswire,
                                           self.server.positive_voting,
                                           self.server.show_publish_as_icon,
                                           full_width_tl_button_header,
                                           self.server.icons_as_buttons,
                                           self.server.rss_icon_at_top,
                                           self.server.publish_button_at_top,
                                           authorized, self.server.theme_name,
                                           self.server.peertube_instances,
                                           allow_local_network_access,
                                           self.server.text_mode_banner,
                                           access_keys,
                                           self.server.system_language,
                                           self.server.max_like_count,
                                           shared_items_federated_domains,
                                           self.server.signing_priv_key_pem,
                                           self.server.cw_lists,
                                           self.server.lists_enabled)
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('text/html', msglen,
                                          cookie, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', '_show_d_ms',
                                            self.server.debug)
                    else:
                        # don't need authorized fetch here because
                        # there is already the authorization check
                        msg = json.dumps(inbox_dm_feed, ensure_ascii=False)
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('application/json',
                                          msglen,
                                          None, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', '_show_d_ms json',
                                            self.server.debug)
                    return True
            else:
                if debug:
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/dm', '')
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if path != '/dm':
            # not the DM inbox
            if debug:
                print('DEBUG: GET access to DM timeline is unauthorized')
            self.send_response(405)
            self.end_headers()
            return True
        return False

    def _show_replies(self, authorized: bool,
                      calling_domain: str, path: str,
                      base_dir: str, http_prefix: str,
                      domain: str, domain_full: str, port: int,
                      onion_domain: str, i2p_domain: str,
                      getreq_start_time,
                      proxy_type: str, cookie: str,
                      debug: str) -> bool:
        """Shows the replies timeline
        """
        if '/users/' in path:
            if authorized:
                inbox_replies_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_FEED, 'tlreplies',
                                    True,
                                    0, self.server.positive_voting,
                                    self.server.voting_time_mins)
                if not inbox_replies_feed:
                    inbox_replies_feed = []
                if self._request_http():
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlreplies', '')
                    page_number = 1
                    if '?page=' in nickname:
                        page_number = nickname.split('?page=')[1]
                        nickname = nickname.split('?page=')[0]
                        if page_number.isdigit():
                            page_number = int(page_number)
                        else:
                            page_number = 1
                    if 'page=' not in path:
                        # if no page was specified then show the first
                        inbox_replies_feed = \
                            person_box_json(self.server.recent_posts_cache,
                                            self.server.session,
                                            base_dir,
                                            domain,
                                            port,
                                            path + '?page=1',
                                            http_prefix,
                                            MAX_POSTS_IN_FEED, 'tlreplies',
                                            True,
                                            0, self.server.positive_voting,
                                            self.server.voting_time_mins)
                    full_width_tl_button_header = \
                        self.server.full_width_tl_button_header
                    minimal_nick = is_minimal(base_dir, domain, nickname)

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = \
                            self.server.key_shortcuts[nickname]

                    shared_items_federated_domains = \
                        self.server.shared_items_federated_domains
                    allow_local_network_access = \
                        self.server.allow_local_network_access
                    twitter_replacement_domain = \
                        self.server.twitter_replacement_domain
                    show_published_date_only = \
                        self.server.show_published_date_only
                    msg = \
                        html_inbox_replies(self.server.css_cache,
                                           self.server.default_timeline,
                                           self.server.recent_posts_cache,
                                           self.server.max_recent_posts,
                                           self.server.translate,
                                           page_number, MAX_POSTS_IN_FEED,
                                           self.server.session,
                                           base_dir,
                                           self.server.cached_webfingers,
                                           self.server.person_cache,
                                           nickname,
                                           domain,
                                           port,
                                           inbox_replies_feed,
                                           self.server.allow_deletion,
                                           http_prefix,
                                           self.server.project_version,
                                           minimal_nick,
                                           self.server.yt_replace_domain,
                                           twitter_replacement_domain,
                                           show_published_date_only,
                                           self.server.newswire,
                                           self.server.positive_voting,
                                           self.server.show_publish_as_icon,
                                           full_width_tl_button_header,
                                           self.server.icons_as_buttons,
                                           self.server.rss_icon_at_top,
                                           self.server.publish_button_at_top,
                                           authorized, self.server.theme_name,
                                           self.server.peertube_instances,
                                           allow_local_network_access,
                                           self.server.text_mode_banner,
                                           access_keys,
                                           self.server.system_language,
                                           self.server.max_like_count,
                                           shared_items_federated_domains,
                                           self.server.signing_priv_key_pem,
                                           self.server.cw_lists,
                                           self.server.lists_enabled)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_replies',
                                        self.server.debug)
                else:
                    # don't need authorized fetch here because there is
                    # already the authorization check
                    msg = json.dumps(inbox_replies_feed,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_replies json',
                                        self.server.debug)
                return True
            else:
                if debug:
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlreplies', '')
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if path != '/tlreplies':
            # not the replies inbox
            if debug:
                print('DEBUG: GET access to inbox is unauthorized')
            self.send_response(405)
            self.end_headers()
            return True
        return False

    def _show_media_timeline(self, authorized: bool,
                             calling_domain: str, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time,
                             proxy_type: str, cookie: str,
                             debug: str) -> bool:
        """Shows the media timeline
        """
        if '/users/' in path:
            if authorized:
                inbox_media_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_MEDIA_FEED, 'tlmedia',
                                    True,
                                    0, self.server.positive_voting,
                                    self.server.voting_time_mins)
                if not inbox_media_feed:
                    inbox_media_feed = []
                if self._request_http():
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlmedia', '')
                    page_number = 1
                    if '?page=' in nickname:
                        page_number = nickname.split('?page=')[1]
                        nickname = nickname.split('?page=')[0]
                        if page_number.isdigit():
                            page_number = int(page_number)
                        else:
                            page_number = 1
                    if 'page=' not in path:
                        # if no page was specified then show the first
                        inbox_media_feed = \
                            person_box_json(self.server.recent_posts_cache,
                                            self.server.session,
                                            base_dir,
                                            domain,
                                            port,
                                            path + '?page=1',
                                            http_prefix,
                                            MAX_POSTS_IN_MEDIA_FEED, 'tlmedia',
                                            True,
                                            0, self.server.positive_voting,
                                            self.server.voting_time_mins)
                    full_width_tl_button_header = \
                        self.server.full_width_tl_button_header
                    minimal_nick = is_minimal(base_dir, domain, nickname)

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = \
                            self.server.key_shortcuts[nickname]
                    fed_domains = \
                        self.server.shared_items_federated_domains
                    allow_local_network_access = \
                        self.server.allow_local_network_access
                    twitter_replacement_domain = \
                        self.server.twitter_replacement_domain
                    msg = \
                        html_inbox_media(self.server.css_cache,
                                         self.server.default_timeline,
                                         self.server.recent_posts_cache,
                                         self.server.max_recent_posts,
                                         self.server.translate,
                                         page_number, MAX_POSTS_IN_MEDIA_FEED,
                                         self.server.session,
                                         base_dir,
                                         self.server.cached_webfingers,
                                         self.server.person_cache,
                                         nickname,
                                         domain,
                                         port,
                                         inbox_media_feed,
                                         self.server.allow_deletion,
                                         http_prefix,
                                         self.server.project_version,
                                         minimal_nick,
                                         self.server.yt_replace_domain,
                                         twitter_replacement_domain,
                                         self.server.show_published_date_only,
                                         self.server.newswire,
                                         self.server.positive_voting,
                                         self.server.show_publish_as_icon,
                                         full_width_tl_button_header,
                                         self.server.icons_as_buttons,
                                         self.server.rss_icon_at_top,
                                         self.server.publish_button_at_top,
                                         authorized,
                                         self.server.theme_name,
                                         self.server.peertube_instances,
                                         allow_local_network_access,
                                         self.server.text_mode_banner,
                                         access_keys,
                                         self.server.system_language,
                                         self.server.max_like_count,
                                         fed_domains,
                                         self.server.signing_priv_key_pem,
                                         self.server.cw_lists,
                                         self.server.lists_enabled)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_media_timeline',
                                        self.server.debug)
                else:
                    # don't need authorized fetch here because there is
                    # already the authorization check
                    msg = json.dumps(inbox_media_feed,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_media_timeline json',
                                        self.server.debug)
                return True
            else:
                if debug:
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlmedia', '')
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if path != '/tlmedia':
            # not the media inbox
            if debug:
                print('DEBUG: GET access to inbox is unauthorized')
            self.send_response(405)
            self.end_headers()
            return True
        return False

    def _show_blogs_timeline(self, authorized: bool,
                             calling_domain: str, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time,
                             proxy_type: str, cookie: str,
                             debug: str) -> bool:
        """Shows the blogs timeline
        """
        if '/users/' in path:
            if authorized:
                inbox_blogs_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_BLOGS_FEED, 'tlblogs',
                                    True,
                                    0, self.server.positive_voting,
                                    self.server.voting_time_mins)
                if not inbox_blogs_feed:
                    inbox_blogs_feed = []
                if self._request_http():
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlblogs', '')
                    page_number = 1
                    if '?page=' in nickname:
                        page_number = nickname.split('?page=')[1]
                        nickname = nickname.split('?page=')[0]
                        if page_number.isdigit():
                            page_number = int(page_number)
                        else:
                            page_number = 1
                    if 'page=' not in path:
                        # if no page was specified then show the first
                        inbox_blogs_feed = \
                            person_box_json(self.server.recent_posts_cache,
                                            self.server.session,
                                            base_dir,
                                            domain,
                                            port,
                                            path + '?page=1',
                                            http_prefix,
                                            MAX_POSTS_IN_BLOGS_FEED, 'tlblogs',
                                            True,
                                            0, self.server.positive_voting,
                                            self.server.voting_time_mins)
                    full_width_tl_button_header = \
                        self.server.full_width_tl_button_header
                    minimal_nick = is_minimal(base_dir, domain, nickname)

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = \
                            self.server.key_shortcuts[nickname]
                    fed_domains = \
                        self.server.shared_items_federated_domains
                    allow_local_network_access = \
                        self.server.allow_local_network_access
                    twitter_replacement_domain = \
                        self.server.twitter_replacement_domain
                    msg = \
                        html_inbox_blogs(self.server.css_cache,
                                         self.server.default_timeline,
                                         self.server.recent_posts_cache,
                                         self.server.max_recent_posts,
                                         self.server.translate,
                                         page_number, MAX_POSTS_IN_BLOGS_FEED,
                                         self.server.session,
                                         base_dir,
                                         self.server.cached_webfingers,
                                         self.server.person_cache,
                                         nickname,
                                         domain,
                                         port,
                                         inbox_blogs_feed,
                                         self.server.allow_deletion,
                                         http_prefix,
                                         self.server.project_version,
                                         minimal_nick,
                                         self.server.yt_replace_domain,
                                         twitter_replacement_domain,
                                         self.server.show_published_date_only,
                                         self.server.newswire,
                                         self.server.positive_voting,
                                         self.server.show_publish_as_icon,
                                         full_width_tl_button_header,
                                         self.server.icons_as_buttons,
                                         self.server.rss_icon_at_top,
                                         self.server.publish_button_at_top,
                                         authorized,
                                         self.server.theme_name,
                                         self.server.peertube_instances,
                                         allow_local_network_access,
                                         self.server.text_mode_banner,
                                         access_keys,
                                         self.server.system_language,
                                         self.server.max_like_count,
                                         fed_domains,
                                         self.server.signing_priv_key_pem,
                                         self.server.cw_lists,
                                         self.server.lists_enabled)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_blogs_timeline',
                                        self.server.debug)
                else:
                    # don't need authorized fetch here because there is
                    # already the authorization check
                    msg = json.dumps(inbox_blogs_feed,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json',
                                      msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_blogs_timeline json',
                                        self.server.debug)
                return True
            else:
                if debug:
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlblogs', '')
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if path != '/tlblogs':
            # not the blogs inbox
            if debug:
                print('DEBUG: GET access to blogs is unauthorized')
            self.send_response(405)
            self.end_headers()
            return True
        return False

    def _show_news_timeline(self, authorized: bool,
                            calling_domain: str, path: str,
                            base_dir: str, http_prefix: str,
                            domain: str, domain_full: str, port: int,
                            onion_domain: str, i2p_domain: str,
                            getreq_start_time,
                            proxy_type: str, cookie: str,
                            debug: str) -> bool:
        """Shows the news timeline
        """
        if '/users/' in path:
            if authorized:
                inbox_news_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_NEWS_FEED, 'tlnews',
                                    True,
                                    self.server.newswire_votes_threshold,
                                    self.server.positive_voting,
                                    self.server.voting_time_mins)
                if not inbox_news_feed:
                    inbox_news_feed = []
                if self._request_http():
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlnews', '')
                    page_number = 1
                    if '?page=' in nickname:
                        page_number = nickname.split('?page=')[1]
                        nickname = nickname.split('?page=')[0]
                        if page_number.isdigit():
                            page_number = int(page_number)
                        else:
                            page_number = 1
                    if 'page=' not in path:
                        newswire_votes_threshold = \
                            self.server.newswire_votes_threshold
                        # if no page was specified then show the first
                        inbox_news_feed = \
                            person_box_json(self.server.recent_posts_cache,
                                            self.server.session,
                                            base_dir,
                                            domain,
                                            port,
                                            path + '?page=1',
                                            http_prefix,
                                            MAX_POSTS_IN_BLOGS_FEED, 'tlnews',
                                            True,
                                            newswire_votes_threshold,
                                            self.server.positive_voting,
                                            self.server.voting_time_mins)
                    curr_nickname = path.split('/users/')[1]
                    if '/' in curr_nickname:
                        curr_nickname = curr_nickname.split('/')[0]
                    moderator = is_moderator(base_dir, curr_nickname)
                    editor = is_editor(base_dir, curr_nickname)
                    artist = is_artist(base_dir, curr_nickname)
                    full_width_tl_button_header = \
                        self.server.full_width_tl_button_header
                    minimal_nick = is_minimal(base_dir, domain, nickname)

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = \
                            self.server.key_shortcuts[nickname]
                    fed_domains = \
                        self.server.shared_items_federated_domains

                    msg = \
                        html_inbox_news(self.server.css_cache,
                                        self.server.default_timeline,
                                        self.server.recent_posts_cache,
                                        self.server.max_recent_posts,
                                        self.server.translate,
                                        page_number, MAX_POSTS_IN_NEWS_FEED,
                                        self.server.session,
                                        base_dir,
                                        self.server.cached_webfingers,
                                        self.server.person_cache,
                                        nickname,
                                        domain,
                                        port,
                                        inbox_news_feed,
                                        self.server.allow_deletion,
                                        http_prefix,
                                        self.server.project_version,
                                        minimal_nick,
                                        self.server.yt_replace_domain,
                                        self.server.twitter_replacement_domain,
                                        self.server.show_published_date_only,
                                        self.server.newswire,
                                        moderator, editor, artist,
                                        self.server.positive_voting,
                                        self.server.show_publish_as_icon,
                                        full_width_tl_button_header,
                                        self.server.icons_as_buttons,
                                        self.server.rss_icon_at_top,
                                        self.server.publish_button_at_top,
                                        authorized,
                                        self.server.theme_name,
                                        self.server.peertube_instances,
                                        self.server.allow_local_network_access,
                                        self.server.text_mode_banner,
                                        access_keys,
                                        self.server.system_language,
                                        self.server.max_like_count,
                                        fed_domains,
                                        self.server.signing_priv_key_pem,
                                        self.server.cw_lists,
                                        self.server.lists_enabled)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_news_timeline',
                                        self.server.debug)
                else:
                    # don't need authorized fetch here because there is
                    # already the authorization check
                    msg = json.dumps(inbox_news_feed,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json',
                                      msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_news_timeline json',
                                        self.server.debug)
                return True
            else:
                if debug:
                    nickname = 'news'
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if path != '/tlnews':
            # not the news inbox
            if debug:
                print('DEBUG: GET access to news is unauthorized')
            self.send_response(405)
            self.end_headers()
            return True
        return False

    def _show_features_timeline(self, authorized: bool,
                                calling_domain: str, path: str,
                                base_dir: str, http_prefix: str,
                                domain: str, domain_full: str, port: int,
                                onion_domain: str, i2p_domain: str,
                                getreq_start_time,
                                proxy_type: str, cookie: str,
                                debug: str) -> bool:
        """Shows the features timeline (all local blogs)
        """
        if '/users/' in path:
            if authorized:
                inbox_features_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_NEWS_FEED, 'tlfeatures',
                                    True,
                                    self.server.newswire_votes_threshold,
                                    self.server.positive_voting,
                                    self.server.voting_time_mins)
                if not inbox_features_feed:
                    inbox_features_feed = []
                if self._request_http():
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlfeatures', '')
                    page_number = 1
                    if '?page=' in nickname:
                        page_number = nickname.split('?page=')[1]
                        nickname = nickname.split('?page=')[0]
                        if page_number.isdigit():
                            page_number = int(page_number)
                        else:
                            page_number = 1
                    if 'page=' not in path:
                        newswire_votes_threshold = \
                            self.server.newswire_votes_threshold
                        # if no page was specified then show the first
                        inbox_features_feed = \
                            person_box_json(self.server.recent_posts_cache,
                                            self.server.session,
                                            base_dir,
                                            domain,
                                            port,
                                            path + '?page=1',
                                            http_prefix,
                                            MAX_POSTS_IN_BLOGS_FEED,
                                            'tlfeatures',
                                            True,
                                            newswire_votes_threshold,
                                            self.server.positive_voting,
                                            self.server.voting_time_mins)
                    curr_nickname = path.split('/users/')[1]
                    if '/' in curr_nickname:
                        curr_nickname = curr_nickname.split('/')[0]
                    full_width_tl_button_header = \
                        self.server.full_width_tl_button_header
                    minimal_nick = is_minimal(base_dir, domain, nickname)

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = \
                            self.server.key_shortcuts[nickname]

                    shared_items_federated_domains = \
                        self.server.shared_items_federated_domains
                    allow_local_network_access = \
                        self.server.allow_local_network_access
                    twitter_replacement_domain = \
                        self.server.twitter_replacement_domain
                    show_published_date_only = \
                        self.server.show_published_date_only
                    msg = \
                        html_inbox_features(self.server.css_cache,
                                            self.server.default_timeline,
                                            self.server.recent_posts_cache,
                                            self.server.max_recent_posts,
                                            self.server.translate,
                                            page_number,
                                            MAX_POSTS_IN_BLOGS_FEED,
                                            self.server.session,
                                            base_dir,
                                            self.server.cached_webfingers,
                                            self.server.person_cache,
                                            nickname,
                                            domain,
                                            port,
                                            inbox_features_feed,
                                            self.server.allow_deletion,
                                            http_prefix,
                                            self.server.project_version,
                                            minimal_nick,
                                            self.server.yt_replace_domain,
                                            twitter_replacement_domain,
                                            show_published_date_only,
                                            self.server.newswire,
                                            self.server.positive_voting,
                                            self.server.show_publish_as_icon,
                                            full_width_tl_button_header,
                                            self.server.icons_as_buttons,
                                            self.server.rss_icon_at_top,
                                            self.server.publish_button_at_top,
                                            authorized,
                                            self.server.theme_name,
                                            self.server.peertube_instances,
                                            allow_local_network_access,
                                            self.server.text_mode_banner,
                                            access_keys,
                                            self.server.system_language,
                                            self.server.max_like_count,
                                            shared_items_federated_domains,
                                            self.server.signing_priv_key_pem,
                                            self.server.cw_lists,
                                            self.server.lists_enabled)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_features_timeline',
                                        self.server.debug)
                else:
                    # don't need authorized fetch here because there is
                    # already the authorization check
                    msg = json.dumps(inbox_features_feed,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json',
                                      msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_features_timeline json',
                                        self.server.debug)
                return True
            else:
                if debug:
                    nickname = 'news'
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if path != '/tlfeatures':
            # not the features inbox
            if debug:
                print('DEBUG: GET access to features is unauthorized')
            self.send_response(405)
            self.end_headers()
            return True
        return False

    def _show_shares_timeline(self, authorized: bool,
                              calling_domain: str, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str, port: int,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              proxy_type: str, cookie: str,
                              debug: str) -> bool:
        """Shows the shares timeline
        """
        if '/users/' in path:
            if authorized:
                if self._request_http():
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlshares', '')
                    page_number = 1
                    if '?page=' in nickname:
                        page_number = nickname.split('?page=')[1]
                        nickname = nickname.split('?page=')[0]
                        if page_number.isdigit():
                            page_number = int(page_number)
                        else:
                            page_number = 1

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = \
                            self.server.key_shortcuts[nickname]
                    full_width_tl_button_header = \
                        self.server.full_width_tl_button_header

                    msg = \
                        html_shares(self.server.css_cache,
                                    self.server.default_timeline,
                                    self.server.recent_posts_cache,
                                    self.server.max_recent_posts,
                                    self.server.translate,
                                    page_number, MAX_POSTS_IN_FEED,
                                    self.server.session,
                                    base_dir,
                                    self.server.cached_webfingers,
                                    self.server.person_cache,
                                    nickname,
                                    domain,
                                    port,
                                    self.server.allow_deletion,
                                    http_prefix,
                                    self.server.project_version,
                                    self.server.yt_replace_domain,
                                    self.server.twitter_replacement_domain,
                                    self.server.show_published_date_only,
                                    self.server.newswire,
                                    self.server.positive_voting,
                                    self.server.show_publish_as_icon,
                                    full_width_tl_button_header,
                                    self.server.icons_as_buttons,
                                    self.server.rss_icon_at_top,
                                    self.server.publish_button_at_top,
                                    authorized, self.server.theme_name,
                                    self.server.peertube_instances,
                                    self.server.allow_local_network_access,
                                    self.server.text_mode_banner,
                                    access_keys,
                                    self.server.system_language,
                                    self.server.max_like_count,
                                    self.server.shared_items_federated_domains,
                                    self.server.signing_priv_key_pem,
                                    self.server.cw_lists,
                                    self.server.lists_enabled)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_shares_timeline',
                                        self.server.debug)
                    return True
        # not the shares timeline
        if debug:
            print('DEBUG: GET access to shares timeline is unauthorized')
        self.send_response(405)
        self.end_headers()
        return True

    def _show_wanted_timeline(self, authorized: bool,
                              calling_domain: str, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str, port: int,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              proxy_type: str, cookie: str,
                              debug: str) -> bool:
        """Shows the wanted timeline
        """
        if '/users/' in path:
            if authorized:
                if self._request_http():
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlwanted', '')
                    page_number = 1
                    if '?page=' in nickname:
                        page_number = nickname.split('?page=')[1]
                        nickname = nickname.split('?page=')[0]
                        if page_number.isdigit():
                            page_number = int(page_number)
                        else:
                            page_number = 1

                    access_keys = self.server.access_keys
                    if self.server.key_shortcuts.get(nickname):
                        access_keys = \
                            self.server.key_shortcuts[nickname]
                    full_width_tl_button_header = \
                        self.server.full_width_tl_button_header
                    msg = \
                        html_wanted(self.server.css_cache,
                                    self.server.default_timeline,
                                    self.server.recent_posts_cache,
                                    self.server.max_recent_posts,
                                    self.server.translate,
                                    page_number, MAX_POSTS_IN_FEED,
                                    self.server.session,
                                    base_dir,
                                    self.server.cached_webfingers,
                                    self.server.person_cache,
                                    nickname,
                                    domain,
                                    port,
                                    self.server.allow_deletion,
                                    http_prefix,
                                    self.server.project_version,
                                    self.server.yt_replace_domain,
                                    self.server.twitter_replacement_domain,
                                    self.server.show_published_date_only,
                                    self.server.newswire,
                                    self.server.positive_voting,
                                    self.server.show_publish_as_icon,
                                    full_width_tl_button_header,
                                    self.server.icons_as_buttons,
                                    self.server.rss_icon_at_top,
                                    self.server.publish_button_at_top,
                                    authorized, self.server.theme_name,
                                    self.server.peertube_instances,
                                    self.server.allow_local_network_access,
                                    self.server.text_mode_banner,
                                    access_keys,
                                    self.server.system_language,
                                    self.server.max_like_count,
                                    self.server.shared_items_federated_domains,
                                    self.server.signing_priv_key_pem,
                                    self.server.cw_lists,
                                    self.server.lists_enabled)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_wanted_timeline',
                                        self.server.debug)
                    return True
        # not the shares timeline
        if debug:
            print('DEBUG: GET access to wanted timeline is unauthorized')
        self.send_response(405)
        self.end_headers()
        return True

    def _show_bookmarks_timeline(self, authorized: bool,
                                 calling_domain: str, path: str,
                                 base_dir: str, http_prefix: str,
                                 domain: str, domain_full: str, port: int,
                                 onion_domain: str, i2p_domain: str,
                                 getreq_start_time,
                                 proxy_type: str, cookie: str,
                                 debug: str) -> bool:
        """Shows the bookmarks timeline
        """
        if '/users/' in path:
            if authorized:
                bookmarks_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_FEED, 'tlbookmarks',
                                    authorized,
                                    0, self.server.positive_voting,
                                    self.server.voting_time_mins)
                if bookmarks_feed:
                    if self._request_http():
                        nickname = path.replace('/users/', '')
                        nickname = nickname.replace('/tlbookmarks', '')
                        nickname = nickname.replace('/bookmarks', '')
                        page_number = 1
                        if '?page=' in nickname:
                            page_number = nickname.split('?page=')[1]
                            nickname = nickname.split('?page=')[0]
                            if page_number.isdigit():
                                page_number = int(page_number)
                            else:
                                page_number = 1
                        if 'page=' not in path:
                            # if no page was specified then show the first
                            bookmarks_feed = \
                                person_box_json(self.server.recent_posts_cache,
                                                self.server.session,
                                                base_dir,
                                                domain,
                                                port,
                                                path + '?page=1',
                                                http_prefix,
                                                MAX_POSTS_IN_FEED,
                                                'tlbookmarks',
                                                authorized,
                                                0, self.server.positive_voting,
                                                self.server.voting_time_mins)
                        full_width_tl_button_header = \
                            self.server.full_width_tl_button_header
                        minimal_nick = is_minimal(base_dir, domain, nickname)

                        access_keys = self.server.access_keys
                        if self.server.key_shortcuts.get(nickname):
                            access_keys = \
                                self.server.key_shortcuts[nickname]

                        shared_items_federated_domains = \
                            self.server.shared_items_federated_domains
                        allow_local_network_access = \
                            self.server.allow_local_network_access
                        twitter_replacement_domain = \
                            self.server.twitter_replacement_domain
                        show_published_date_only = \
                            self.server.show_published_date_only
                        msg = \
                            html_bookmarks(self.server.css_cache,
                                           self.server.default_timeline,
                                           self.server.recent_posts_cache,
                                           self.server.max_recent_posts,
                                           self.server.translate,
                                           page_number, MAX_POSTS_IN_FEED,
                                           self.server.session,
                                           base_dir,
                                           self.server.cached_webfingers,
                                           self.server.person_cache,
                                           nickname,
                                           domain,
                                           port,
                                           bookmarks_feed,
                                           self.server.allow_deletion,
                                           http_prefix,
                                           self.server.project_version,
                                           minimal_nick,
                                           self.server.yt_replace_domain,
                                           twitter_replacement_domain,
                                           show_published_date_only,
                                           self.server.newswire,
                                           self.server.positive_voting,
                                           self.server.show_publish_as_icon,
                                           full_width_tl_button_header,
                                           self.server.icons_as_buttons,
                                           self.server.rss_icon_at_top,
                                           self.server.publish_button_at_top,
                                           authorized,
                                           self.server.theme_name,
                                           self.server.peertube_instances,
                                           allow_local_network_access,
                                           self.server.text_mode_banner,
                                           access_keys,
                                           self.server.system_language,
                                           self.server.max_like_count,
                                           shared_items_federated_domains,
                                           self.server.signing_priv_key_pem,
                                           self.server.cw_lists,
                                           self.server.lists_enabled)
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('text/html', msglen,
                                          cookie, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', '_show_bookmarks_timeline',
                                            self.server.debug)
                    else:
                        # don't need authorized fetch here because
                        # there is already the authorization check
                        msg = json.dumps(bookmarks_feed,
                                         ensure_ascii=False)
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('application/json', msglen,
                                          None, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET',
                                            '_show_bookmarks_timeline json',
                                            self.server.debug)
                    return True
            else:
                if debug:
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/tlbookmarks', '')
                    nickname = nickname.replace('/bookmarks', '')
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if debug:
            print('DEBUG: GET access to bookmarks is unauthorized')
        self.send_response(405)
        self.end_headers()
        return True

    def _show_outbox_timeline(self, authorized: bool,
                              calling_domain: str, path: str,
                              base_dir: str, http_prefix: str,
                              domain: str, domain_full: str, port: int,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time,
                              proxy_type: str, cookie: str,
                              debug: str) -> bool:
        """Shows the outbox timeline
        """
        # get outbox feed for a person
        outbox_feed = \
            person_box_json(self.server.recent_posts_cache,
                            self.server.session,
                            base_dir, domain, port, path,
                            http_prefix, MAX_POSTS_IN_FEED, 'outbox',
                            authorized,
                            self.server.newswire_votes_threshold,
                            self.server.positive_voting,
                            self.server.voting_time_mins)
        if outbox_feed:
            nickname = \
                path.replace('/users/', '').replace('/outbox', '')
            page_number = 0
            if '?page=' in nickname:
                page_number = nickname.split('?page=')[1]
                nickname = nickname.split('?page=')[0]
                if page_number.isdigit():
                    page_number = int(page_number)
                else:
                    page_number = 1
            else:
                if self._request_http():
                    page_number = 1
            if authorized and page_number >= 1:
                # if a page wasn't specified then show the first one
                page_str = '?page=' + str(page_number)
                outbox_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir, domain, port,
                                    path + page_str,
                                    http_prefix,
                                    MAX_POSTS_IN_FEED, 'outbox',
                                    authorized,
                                    self.server.newswire_votes_threshold,
                                    self.server.positive_voting,
                                    self.server.voting_time_mins)
            else:
                page_number = 1

            if self._request_http():
                full_width_tl_button_header = \
                    self.server.full_width_tl_button_header
                minimal_nick = is_minimal(base_dir, domain, nickname)

                access_keys = self.server.access_keys
                if self.server.key_shortcuts.get(nickname):
                    access_keys = \
                        self.server.key_shortcuts[nickname]

                msg = \
                    html_outbox(self.server.css_cache,
                                self.server.default_timeline,
                                self.server.recent_posts_cache,
                                self.server.max_recent_posts,
                                self.server.translate,
                                page_number, MAX_POSTS_IN_FEED,
                                self.server.session,
                                base_dir,
                                self.server.cached_webfingers,
                                self.server.person_cache,
                                nickname, domain, port,
                                outbox_feed,
                                self.server.allow_deletion,
                                http_prefix,
                                self.server.project_version,
                                minimal_nick,
                                self.server.yt_replace_domain,
                                self.server.twitter_replacement_domain,
                                self.server.show_published_date_only,
                                self.server.newswire,
                                self.server.positive_voting,
                                self.server.show_publish_as_icon,
                                full_width_tl_button_header,
                                self.server.icons_as_buttons,
                                self.server.rss_icon_at_top,
                                self.server.publish_button_at_top,
                                authorized,
                                self.server.theme_name,
                                self.server.peertube_instances,
                                self.server.allow_local_network_access,
                                self.server.text_mode_banner,
                                access_keys,
                                self.server.system_language,
                                self.server.max_like_count,
                                self.server.shared_items_federated_domains,
                                self.server.signing_priv_key_pem,
                                self.server.cw_lists,
                                self.server.lists_enabled)
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time,
                                    self.server.fitness,
                                    '_GET', '_show_outbox_timeline',
                                    self.server.debug)
            else:
                if self._secure_mode():
                    msg = json.dumps(outbox_feed,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_outbox_timeline json',
                                        self.server.debug)
                else:
                    self._404()
            return True
        return False

    def _show_mod_timeline(self, authorized: bool,
                           calling_domain: str, path: str,
                           base_dir: str, http_prefix: str,
                           domain: str, domain_full: str, port: int,
                           onion_domain: str, i2p_domain: str,
                           getreq_start_time,
                           proxy_type: str, cookie: str,
                           debug: str) -> bool:
        """Shows the moderation timeline
        """
        if '/users/' in path:
            if authorized:
                moderation_feed = \
                    person_box_json(self.server.recent_posts_cache,
                                    self.server.session,
                                    base_dir,
                                    domain,
                                    port,
                                    path,
                                    http_prefix,
                                    MAX_POSTS_IN_FEED, 'moderation',
                                    True,
                                    0, self.server.positive_voting,
                                    self.server.voting_time_mins)
                if moderation_feed:
                    if self._request_http():
                        nickname = path.replace('/users/', '')
                        nickname = nickname.replace('/moderation', '')
                        page_number = 1
                        if '?page=' in nickname:
                            page_number = nickname.split('?page=')[1]
                            nickname = nickname.split('?page=')[0]
                            if page_number.isdigit():
                                page_number = int(page_number)
                            else:
                                page_number = 1
                        if 'page=' not in path:
                            # if no page was specified then show the first
                            moderation_feed = \
                                person_box_json(self.server.recent_posts_cache,
                                                self.server.session,
                                                base_dir,
                                                domain,
                                                port,
                                                path + '?page=1',
                                                http_prefix,
                                                MAX_POSTS_IN_FEED,
                                                'moderation',
                                                True,
                                                0, self.server.positive_voting,
                                                self.server.voting_time_mins)
                        full_width_tl_button_header = \
                            self.server.full_width_tl_button_header
                        moderation_action_str = ''

                        access_keys = self.server.access_keys
                        if self.server.key_shortcuts.get(nickname):
                            access_keys = \
                                self.server.key_shortcuts[nickname]

                        shared_items_federated_domains = \
                            self.server.shared_items_federated_domains
                        twitter_replacement_domain = \
                            self.server.twitter_replacement_domain
                        allow_local_network_access = \
                            self.server.allow_local_network_access
                        show_published_date_only = \
                            self.server.show_published_date_only
                        msg = \
                            html_moderation(self.server.css_cache,
                                            self.server.default_timeline,
                                            self.server.recent_posts_cache,
                                            self.server.max_recent_posts,
                                            self.server.translate,
                                            page_number, MAX_POSTS_IN_FEED,
                                            self.server.session,
                                            base_dir,
                                            self.server.cached_webfingers,
                                            self.server.person_cache,
                                            nickname,
                                            domain,
                                            port,
                                            moderation_feed,
                                            True,
                                            http_prefix,
                                            self.server.project_version,
                                            self.server.yt_replace_domain,
                                            twitter_replacement_domain,
                                            show_published_date_only,
                                            self.server.newswire,
                                            self.server.positive_voting,
                                            self.server.show_publish_as_icon,
                                            full_width_tl_button_header,
                                            self.server.icons_as_buttons,
                                            self.server.rss_icon_at_top,
                                            self.server.publish_button_at_top,
                                            authorized, moderation_action_str,
                                            self.server.theme_name,
                                            self.server.peertube_instances,
                                            allow_local_network_access,
                                            self.server.text_mode_banner,
                                            access_keys,
                                            self.server.system_language,
                                            self.server.max_like_count,
                                            shared_items_federated_domains,
                                            self.server.signing_priv_key_pem,
                                            self.server.cw_lists,
                                            self.server.lists_enabled)
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('text/html', msglen,
                                          cookie, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', '_show_mod_timeline',
                                            self.server.debug)
                    else:
                        # don't need authorized fetch here because
                        # there is already the authorization check
                        msg = json.dumps(moderation_feed,
                                         ensure_ascii=False)
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('application/json', msglen,
                                          None, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', '_show_mod_timeline json',
                                            self.server.debug)
                    return True
            else:
                if debug:
                    nickname = path.replace('/users/', '')
                    nickname = nickname.replace('/moderation', '')
                    print('DEBUG: ' + nickname +
                          ' was not authorized to access ' + path)
        if debug:
            print('DEBUG: GET access to moderation feed is unauthorized')
        self.send_response(405)
        self.end_headers()
        return True

    def _show_shares_feed(self, authorized: bool,
                          calling_domain: str, path: str,
                          base_dir: str, http_prefix: str,
                          domain: str, domain_full: str, port: int,
                          onion_domain: str, i2p_domain: str,
                          getreq_start_time,
                          proxy_type: str, cookie: str,
                          debug: str, shares_file_type: str) -> bool:
        """Shows the shares feed
        """
        shares = \
            get_shares_feed_for_person(base_dir, domain, port, path,
                                       http_prefix, shares_file_type,
                                       SHARES_PER_PAGE)
        if shares:
            if self._request_http():
                page_number = 1
                if '?page=' not in path:
                    search_path = path
                    # get a page of shares, not the summary
                    shares = \
                        get_shares_feed_for_person(base_dir, domain, port,
                                                   path + '?page=true',
                                                   http_prefix,
                                                   shares_file_type,
                                                   SHARES_PER_PAGE)
                else:
                    page_number_str = path.split('?page=')[1]
                    if '#' in page_number_str:
                        page_number_str = page_number_str.split('#')[0]
                    if page_number_str.isdigit():
                        page_number = int(page_number_str)
                    search_path = path.split('?page=')[0]
                search_path2 = search_path.replace('/' + shares_file_type, '')
                get_person = person_lookup(domain, search_path2, base_dir)
                if get_person:
                    if not self._establish_session("show_shares_feed"):
                        self._404()
                        self.server.getreq_busy = False
                        return True

                    access_keys = self.server.access_keys
                    if '/users/' in path:
                        nickname = path.split('/users/')[1]
                        if '/' in nickname:
                            nickname = nickname.split('/')[0]
                        if self.server.key_shortcuts.get(nickname):
                            access_keys = \
                                self.server.key_shortcuts[nickname]

                    city = get_spoofed_city(self.server.city,
                                            base_dir, nickname, domain)
                    shared_items_federated_domains = \
                        self.server.shared_items_federated_domains
                    msg = \
                        html_profile(self.server.signing_priv_key_pem,
                                     self.server.rss_icon_at_top,
                                     self.server.css_cache,
                                     self.server.icons_as_buttons,
                                     self.server.default_timeline,
                                     self.server.recent_posts_cache,
                                     self.server.max_recent_posts,
                                     self.server.translate,
                                     self.server.project_version,
                                     base_dir, http_prefix,
                                     authorized,
                                     get_person, shares_file_type,
                                     self.server.session,
                                     self.server.cached_webfingers,
                                     self.server.person_cache,
                                     self.server.yt_replace_domain,
                                     self.server.twitter_replacement_domain,
                                     self.server.show_published_date_only,
                                     self.server.newswire,
                                     self.server.theme_name,
                                     self.server.dormant_months,
                                     self.server.peertube_instances,
                                     self.server.allow_local_network_access,
                                     self.server.text_mode_banner,
                                     self.server.debug,
                                     access_keys, city,
                                     self.server.system_language,
                                     self.server.max_like_count,
                                     shared_items_federated_domains,
                                     shares,
                                     page_number, SHARES_PER_PAGE,
                                     self.server.cw_lists,
                                     self.server.lists_enabled,
                                     self.server.content_license_url)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_shares_feed',
                                        self.server.debug)
                    self.server.getreq_busy = False
                    return True
            else:
                if self._secure_mode():
                    msg = json.dumps(shares,
                                     ensure_ascii=False)
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_shares_feed json',
                                        self.server.debug)
                else:
                    self._404()
                return True
        return False

    def _show_following_feed(self, authorized: bool,
                             calling_domain: str, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time,
                             proxy_type: str, cookie: str,
                             debug: str) -> bool:
        """Shows the following feed
        """
        following = \
            get_following_feed(base_dir, domain, port, path,
                               http_prefix, authorized, FOLLOWS_PER_PAGE,
                               'following')
        if following:
            if self._request_http():
                page_number = 1
                if '?page=' not in path:
                    search_path = path
                    # get a page of following, not the summary
                    following = \
                        get_following_feed(base_dir,
                                           domain,
                                           port,
                                           path + '?page=true',
                                           http_prefix,
                                           authorized, FOLLOWS_PER_PAGE)
                else:
                    page_number_str = path.split('?page=')[1]
                    if '#' in page_number_str:
                        page_number_str = page_number_str.split('#')[0]
                    if page_number_str.isdigit():
                        page_number = int(page_number_str)
                    search_path = path.split('?page=')[0]
                get_person = \
                    person_lookup(domain,
                                  search_path.replace('/following', ''),
                                  base_dir)
                if get_person:
                    if not self._establish_session("show_following_feed"):
                        self._404()
                        return True

                    access_keys = self.server.access_keys
                    city = None
                    if '/users/' in path:
                        nickname = path.split('/users/')[1]
                        if '/' in nickname:
                            nickname = nickname.split('/')[0]
                        if self.server.key_shortcuts.get(nickname):
                            access_keys = \
                                self.server.key_shortcuts[nickname]

                        city = get_spoofed_city(self.server.city,
                                                base_dir, nickname, domain)
                    content_license_url = \
                        self.server.content_license_url
                    shared_items_federated_domains = \
                        self.server.shared_items_federated_domains
                    msg = \
                        html_profile(self.server.signing_priv_key_pem,
                                     self.server.rss_icon_at_top,
                                     self.server.css_cache,
                                     self.server.icons_as_buttons,
                                     self.server.default_timeline,
                                     self.server.recent_posts_cache,
                                     self.server.max_recent_posts,
                                     self.server.translate,
                                     self.server.project_version,
                                     base_dir, http_prefix,
                                     authorized,
                                     get_person, 'following',
                                     self.server.session,
                                     self.server.cached_webfingers,
                                     self.server.person_cache,
                                     self.server.yt_replace_domain,
                                     self.server.twitter_replacement_domain,
                                     self.server.show_published_date_only,
                                     self.server.newswire,
                                     self.server.theme_name,
                                     self.server.dormant_months,
                                     self.server.peertube_instances,
                                     self.server.allow_local_network_access,
                                     self.server.text_mode_banner,
                                     self.server.debug,
                                     access_keys, city,
                                     self.server.system_language,
                                     self.server.max_like_count,
                                     shared_items_federated_domains,
                                     following,
                                     page_number,
                                     FOLLOWS_PER_PAGE,
                                     self.server.cw_lists,
                                     self.server.lists_enabled,
                                     content_license_url).encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html',
                                      msglen, cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_following_feed',
                                        self.server.debug)
                    return True
            else:
                if self._secure_mode():
                    msg = json.dumps(following,
                                     ensure_ascii=False).encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_following_feed json',
                                        self.server.debug)
                else:
                    self._404()
                return True
        return False

    def _show_followers_feed(self, authorized: bool,
                             calling_domain: str, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time,
                             proxy_type: str, cookie: str,
                             debug: str) -> bool:
        """Shows the followers feed
        """
        followers = \
            get_following_feed(base_dir, domain, port, path, http_prefix,
                               authorized, FOLLOWS_PER_PAGE, 'followers')
        if followers:
            if self._request_http():
                page_number = 1
                if '?page=' not in path:
                    search_path = path
                    # get a page of followers, not the summary
                    followers = \
                        get_following_feed(base_dir,
                                           domain,
                                           port,
                                           path + '?page=1',
                                           http_prefix,
                                           authorized, FOLLOWS_PER_PAGE,
                                           'followers')
                else:
                    page_number_str = path.split('?page=')[1]
                    if '#' in page_number_str:
                        page_number_str = page_number_str.split('#')[0]
                    if page_number_str.isdigit():
                        page_number = int(page_number_str)
                    search_path = path.split('?page=')[0]
                get_person = \
                    person_lookup(domain,
                                  search_path.replace('/followers', ''),
                                  base_dir)
                if get_person:
                    if not self._establish_session("show_followers_feed"):
                        self._404()
                        return True

                    access_keys = self.server.access_keys
                    city = None
                    if '/users/' in path:
                        nickname = path.split('/users/')[1]
                        if '/' in nickname:
                            nickname = nickname.split('/')[0]
                        if self.server.key_shortcuts.get(nickname):
                            access_keys = \
                                self.server.key_shortcuts[nickname]

                        city = get_spoofed_city(self.server.city,
                                                base_dir, nickname, domain)
                    content_license_url = \
                        self.server.content_license_url
                    shared_items_federated_domains = \
                        self.server.shared_items_federated_domains
                    msg = \
                        html_profile(self.server.signing_priv_key_pem,
                                     self.server.rss_icon_at_top,
                                     self.server.css_cache,
                                     self.server.icons_as_buttons,
                                     self.server.default_timeline,
                                     self.server.recent_posts_cache,
                                     self.server.max_recent_posts,
                                     self.server.translate,
                                     self.server.project_version,
                                     base_dir,
                                     http_prefix,
                                     authorized,
                                     get_person, 'followers',
                                     self.server.session,
                                     self.server.cached_webfingers,
                                     self.server.person_cache,
                                     self.server.yt_replace_domain,
                                     self.server.twitter_replacement_domain,
                                     self.server.show_published_date_only,
                                     self.server.newswire,
                                     self.server.theme_name,
                                     self.server.dormant_months,
                                     self.server.peertube_instances,
                                     self.server.allow_local_network_access,
                                     self.server.text_mode_banner,
                                     self.server.debug,
                                     access_keys, city,
                                     self.server.system_language,
                                     self.server.max_like_count,
                                     shared_items_federated_domains,
                                     followers,
                                     page_number,
                                     FOLLOWS_PER_PAGE,
                                     self.server.cw_lists,
                                     self.server.lists_enabled,
                                     content_license_url).encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_followers_feed',
                                        self.server.debug)
                    return True
            else:
                if self._secure_mode():
                    msg = json.dumps(followers,
                                     ensure_ascii=False).encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET', '_show_followers_feed json',
                                        self.server.debug)
                else:
                    self._404()
            return True
        return False

    def _get_featured_collection(self, calling_domain: str,
                                 base_dir: str, path: str,
                                 http_prefix: str,
                                 nickname: str, domain: str,
                                 domain_full: str,
                                 system_language: str) -> None:
        """Returns the featured posts collections in
        actor/collections/featured
        """
        featured_collection = \
            json_pin_post(base_dir, http_prefix,
                          nickname, domain, domain_full, system_language)
        msg = json.dumps(featured_collection,
                         ensure_ascii=False).encode('utf-8')
        msglen = len(msg)
        self._set_headers('application/json', msglen,
                          None, calling_domain, False)
        self._write(msg)

    def _get_featured_tags_collection(self, calling_domain: str,
                                      path: str,
                                      http_prefix: str,
                                      domain_full: str):
        """Returns the featured tags collections in
        actor/collections/featuredTags
        TODO add ability to set a featured tags
        """
        post_context = get_individual_post_context()
        featured_tags_collection = {
            '@context': post_context,
            'id': http_prefix + '://' + domain_full + path,
            'orderedItems': [],
            'totalItems': 0,
            'type': 'OrderedCollection'
        }
        msg = json.dumps(featured_tags_collection,
                         ensure_ascii=False).encode('utf-8')
        msglen = len(msg)
        self._set_headers('application/json', msglen,
                          None, calling_domain, False)
        self._write(msg)

    def _show_person_profile(self, authorized: bool,
                             calling_domain: str, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time,
                             proxy_type: str, cookie: str,
                             debug: str) -> bool:
        """Shows the profile for a person
        """
        # look up a person
        actor_json = person_lookup(domain, path, base_dir)
        if not actor_json:
            return False
        if self._request_http():
            if not self._establish_session("showPersonProfile"):
                self._404()
                return True

            access_keys = self.server.access_keys
            city = None
            if '/users/' in path:
                nickname = path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]
                if self.server.key_shortcuts.get(nickname):
                    access_keys = \
                        self.server.key_shortcuts[nickname]

                city = get_spoofed_city(self.server.city,
                                        base_dir, nickname, domain)
            msg = \
                html_profile(self.server.signing_priv_key_pem,
                             self.server.rss_icon_at_top,
                             self.server.css_cache,
                             self.server.icons_as_buttons,
                             self.server.default_timeline,
                             self.server.recent_posts_cache,
                             self.server.max_recent_posts,
                             self.server.translate,
                             self.server.project_version,
                             base_dir,
                             http_prefix,
                             authorized,
                             actor_json, 'posts',
                             self.server.session,
                             self.server.cached_webfingers,
                             self.server.person_cache,
                             self.server.yt_replace_domain,
                             self.server.twitter_replacement_domain,
                             self.server.show_published_date_only,
                             self.server.newswire,
                             self.server.theme_name,
                             self.server.dormant_months,
                             self.server.peertube_instances,
                             self.server.allow_local_network_access,
                             self.server.text_mode_banner,
                             self.server.debug,
                             access_keys, city,
                             self.server.system_language,
                             self.server.max_like_count,
                             self.server.shared_items_federated_domains,
                             None, None, None,
                             self.server.cw_lists,
                             self.server.lists_enabled,
                             self.server.content_license_url).encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time,
                                self.server.fitness,
                                '_GET', '_show_person_profile',
                                self.server.debug)
        else:
            if self._secure_mode():
                accept_str = self.headers['Accept']
                msg_str = json.dumps(actor_json, ensure_ascii=False)
                msg = msg_str.encode('utf-8')
                msglen = len(msg)
                if 'application/ld+json' in accept_str:
                    self._set_headers('application/ld+json', msglen,
                                      cookie, calling_domain, False)
                elif 'application/jrd+json' in accept_str:
                    self._set_headers('application/jrd+json', msglen,
                                      cookie, calling_domain, False)
                else:
                    self._set_headers('application/activity+json', msglen,
                                      cookie, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time,
                                    self.server.fitness,
                                    '_GET', '_show_person_profile json',
                                    self.server.debug)
            else:
                self._404()
        return True

    def _show_instance_actor(self, calling_domain: str, path: str,
                             base_dir: str, http_prefix: str,
                             domain: str, domain_full: str, port: int,
                             onion_domain: str, i2p_domain: str,
                             getreq_start_time,
                             proxy_type: str, cookie: str,
                             debug: str,
                             enable_shared_inbox: bool) -> bool:
        """Shows the instance actor
        """
        if debug:
            print('Instance actor requested by ' + calling_domain)
        if self._request_http():
            self._404()
            return False
        actor_json = person_lookup(domain, path, base_dir)
        if not actor_json:
            print('ERROR: no instance actor found')
            self._404()
            return False
        accept_str = self.headers['Accept']
        if onion_domain and calling_domain.endswith('.onion'):
            actor_domain_url = 'http://' + onion_domain
        elif i2p_domain and calling_domain.endswith('.i2p'):
            actor_domain_url = 'http://' + i2p_domain
        else:
            actor_domain_url = http_prefix + '://' + domain_full
        actor_url = actor_domain_url + '/users/Actor'
        remove_fields = (
            'icon', 'image', 'tts', 'shares',
            'alsoKnownAs', 'hasOccupation', 'featured',
            'featuredTags', 'discoverable', 'published',
            'devices'
        )
        for rfield in remove_fields:
            if rfield in actor_json:
                del actor_json[rfield]
        actor_json['endpoints'] = {}
        if enable_shared_inbox:
            actor_json['endpoints'] = {
                'sharedInbox': actor_domain_url + '/inbox'
            }
        actor_json['name'] = 'ACTOR'
        actor_json['preferredUsername'] = domain_full
        actor_json['id'] = actor_domain_url + '/actor'
        actor_json['type'] = 'Application'
        actor_json['summary'] = 'Instance Actor'
        actor_json['publicKey']['id'] = actor_domain_url + '/actor#main-key'
        actor_json['publicKey']['owner'] = actor_domain_url + '/actor'
        actor_json['url'] = actor_domain_url + '/actor'
        actor_json['inbox'] = actor_url + '/inbox'
        actor_json['followers'] = actor_url + '/followers'
        actor_json['following'] = actor_url + '/following'
        msg_str = json.dumps(actor_json, ensure_ascii=False)
        if onion_domain and calling_domain.endswith('.onion'):
            msg_str = msg_str.replace(http_prefix + '://' + domain_full,
                                      'http://' + onion_domain)
        elif i2p_domain and calling_domain.endswith('.i2p'):
            msg_str = msg_str.replace(http_prefix + '://' + domain_full,
                                      'http://' + i2p_domain)
        msg = msg_str.encode('utf-8')
        msglen = len(msg)
        if 'application/ld+json' in accept_str:
            self._set_headers('application/ld+json', msglen,
                              cookie, calling_domain, False)
        elif 'application/jrd+json' in accept_str:
            self._set_headers('application/jrd+json', msglen,
                              cookie, calling_domain, False)
        else:
            self._set_headers('application/activity+json', msglen,
                              cookie, calling_domain, False)
        self._write(msg)
        fitness_performance(getreq_start_time,
                            self.server.fitness,
                            '_GET', '_show_instance_actor',
                            self.server.debug)
        return True

    def _show_blog_page(self, authorized: bool,
                        calling_domain: str, path: str,
                        base_dir: str, http_prefix: str,
                        domain: str, domain_full: str, port: int,
                        onion_domain: str, i2p_domain: str,
                        getreq_start_time,
                        proxy_type: str, cookie: str,
                        translate: {}, debug: str) -> bool:
        """Shows a blog page
        """
        page_number = 1
        nickname = path.split('/blog/')[1]
        if '/' in nickname:
            nickname = nickname.split('/')[0]
        if '?' in nickname:
            nickname = nickname.split('?')[0]
        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
                if page_number < 1:
                    page_number = 1
                elif page_number > 10:
                    page_number = 10
        if not self._establish_session("showBlogPage"):
            self._404()
            self.server.getreq_busy = False
            return True
        msg = html_blog_page(authorized,
                             self.server.session,
                             base_dir,
                             http_prefix,
                             translate,
                             nickname,
                             domain, port,
                             MAX_POSTS_IN_BLOGS_FEED, page_number,
                             self.server.peertube_instances,
                             self.server.system_language,
                             self.server.person_cache,
                             self.server.debug)
        if msg is not None:
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time,
                                self.server.fitness,
                                '_GET', '_show_blog_page',
                                self.server.debug)
            return True
        self._404()
        return True

    def _redirect_to_login_screen(self, calling_domain: str, path: str,
                                  http_prefix: str, domain_full: str,
                                  onion_domain: str, i2p_domain: str,
                                  getreq_start_time,
                                  authorized: bool, debug: bool):
        """Redirects to the login screen if necessary
        """
        divert_to_login_screen = False
        if '/media/' not in path and \
           '/ontologies/' not in path and \
           '/data/' not in path and \
           '/sharefiles/' not in path and \
           '/statuses/' not in path and \
           '/emoji/' not in path and \
           '/tags/' not in path and \
           '/avatars/' not in path and \
           '/favicons/' not in path and \
           '/headers/' not in path and \
           '/fonts/' not in path and \
           '/icons/' not in path:
            divert_to_login_screen = True
            if path.startswith('/users/'):
                nick_str = path.split('/users/')[1]
                if '/' not in nick_str and '?' not in nick_str:
                    divert_to_login_screen = False
                else:
                    if path.endswith('/following') or \
                       path.endswith('/followers') or \
                       path.endswith('/skills') or \
                       path.endswith('/roles') or \
                       path.endswith('/wanted') or \
                       path.endswith('/shares'):
                        divert_to_login_screen = False

        if divert_to_login_screen and not authorized:
            divert_path = '/login'
            if self.server.news_instance:
                # for news instances if not logged in then show the
                # front page
                divert_path = '/users/news'
            # if debug:
            print('DEBUG: divert_to_login_screen=' +
                  str(divert_to_login_screen))
            print('DEBUG: authorized=' + str(authorized))
            print('DEBUG: path=' + path)
            if calling_domain.endswith('.onion') and onion_domain:
                self._redirect_headers('http://' +
                                       onion_domain + divert_path,
                                       None, calling_domain)
            elif calling_domain.endswith('.i2p') and i2p_domain:
                self._redirect_headers('http://' +
                                       i2p_domain + divert_path,
                                       None, calling_domain)
            else:
                self._redirect_headers(http_prefix + '://' +
                                       domain_full +
                                       divert_path, None, calling_domain)
            fitness_performance(getreq_start_time,
                                self.server.fitness,
                                '_GET', '_redirect_to_login_screen',
                                self.server.debug)
            return True
        return False

    def _get_style_sheet(self, calling_domain: str, path: str,
                         getreq_start_time) -> bool:
        """Returns the content of a css file
        """
        # get the last part of the path
        # eg. /my/path/file.css becomes file.css
        if '/' in path:
            path = path.split('/')[-1]
        if os.path.isfile(path):
            tries = 0
            while tries < 5:
                try:
                    css = get_css(self.server.base_dir, path,
                                  self.server.css_cache)
                    if css:
                        break
                except BaseException as ex:
                    print('EX: _get_style_sheet ' +
                          str(tries) + ' ' + str(ex))
                    time.sleep(1)
                    tries += 1
            msg = css.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/css', msglen,
                              None, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time,
                                self.server.fitness,
                                '_GET', '_get_style_sheet',
                                self.server.debug)
            return True
        self._404()
        return True

    def _show_q_rcode(self, calling_domain: str, path: str,
                      base_dir: str, domain: str, port: int,
                      getreq_start_time) -> bool:
        """Shows a QR code for an account
        """
        nickname = get_nickname_from_actor(path)
        save_person_qrcode(base_dir, nickname, domain, port)
        qr_filename = \
            acct_dir(base_dir, nickname, domain) + '/qrcode.png'
        if os.path.isfile(qr_filename):
            if self._etag_exists(qr_filename):
                # The file has not changed
                self._304()
                return

            tries = 0
            media_binary = None
            while tries < 5:
                try:
                    with open(qr_filename, 'rb') as av_file:
                        media_binary = av_file.read()
                        break
                except BaseException as ex:
                    print('EX: _show_q_rcode ' + str(tries) + ' ' + str(ex))
                    time.sleep(1)
                    tries += 1
            if media_binary:
                mime_type = media_file_mime_type(qr_filename)
                self._set_headers_etag(qr_filename, mime_type,
                                       media_binary, None,
                                       self.server.domain_full,
                                       False, None)
                self._write(media_binary)
                fitness_performance(getreq_start_time,
                                    self.server.fitness,
                                    '_GET', '_show_q_rcode',
                                    self.server.debug)
                return True
        self._404()
        return True

    def _search_screen_banner(self, calling_domain: str, path: str,
                              base_dir: str, domain: str, port: int,
                              getreq_start_time) -> bool:
        """Shows a banner image on the search screen
        """
        nickname = get_nickname_from_actor(path)
        banner_filename = \
            acct_dir(base_dir, nickname, domain) + '/search_banner.png'
        if not os.path.isfile(banner_filename):
            if os.path.isfile(base_dir + '/theme/default/search_banner.png'):
                copyfile(base_dir + '/theme/default/search_banner.png',
                         banner_filename)
        if os.path.isfile(banner_filename):
            if self._etag_exists(banner_filename):
                # The file has not changed
                self._304()
                return True

            tries = 0
            media_binary = None
            while tries < 5:
                try:
                    with open(banner_filename, 'rb') as av_file:
                        media_binary = av_file.read()
                        break
                except BaseException as ex:
                    print('EX: _search_screen_banner ' +
                          str(tries) + ' ' + str(ex))
                    time.sleep(1)
                    tries += 1
            if media_binary:
                mime_type = media_file_mime_type(banner_filename)
                self._set_headers_etag(banner_filename, mime_type,
                                       media_binary, None,
                                       self.server.domain_full,
                                       False, None)
                self._write(media_binary)
                fitness_performance(getreq_start_time,
                                    self.server.fitness,
                                    '_GET', '_search_screen_banner',
                                    self.server.debug)
                return True
        self._404()
        return True

    def _column_image(self, side: str, calling_domain: str, path: str,
                      base_dir: str, domain: str, port: int,
                      getreq_start_time) -> bool:
        """Shows an image at the top of the left/right column
        """
        nickname = get_nickname_from_actor(path)
        if not nickname:
            self._404()
            return True
        banner_filename = \
            acct_dir(base_dir, nickname, domain) + '/' + \
            side + '_col_image.png'
        if os.path.isfile(banner_filename):
            if self._etag_exists(banner_filename):
                # The file has not changed
                self._304()
                return True

            tries = 0
            media_binary = None
            while tries < 5:
                try:
                    with open(banner_filename, 'rb') as av_file:
                        media_binary = av_file.read()
                        break
                except BaseException as ex:
                    print('EX: _column_image ' + str(tries) + ' ' + str(ex))
                    time.sleep(1)
                    tries += 1
            if media_binary:
                mime_type = media_file_mime_type(banner_filename)
                self._set_headers_etag(banner_filename, mime_type,
                                       media_binary, None,
                                       self.server.domain_full,
                                       False, None)
                self._write(media_binary)
                fitness_performance(getreq_start_time,
                                    self.server.fitness,
                                    '_GET', '_column_image ' + side,
                                    self.server.debug)
                return True
        self._404()
        return True

    def _show_background_image(self, calling_domain: str, path: str,
                               base_dir: str, getreq_start_time) -> bool:
        """Show a background image
        """
        image_extensions = get_image_extensions()
        for ext in image_extensions:
            for bg in ('follow', 'options', 'login', 'welcome'):
                # follow screen background image
                if path.endswith('/' + bg + '-background.' + ext):
                    bg_filename = \
                        base_dir + '/accounts/' + \
                        bg + '-background.' + ext
                    if os.path.isfile(bg_filename):
                        if self._etag_exists(bg_filename):
                            # The file has not changed
                            self._304()
                            return True

                        tries = 0
                        bg_binary = None
                        while tries < 5:
                            try:
                                with open(bg_filename, 'rb') as av_file:
                                    bg_binary = av_file.read()
                                    break
                            except BaseException as ex:
                                print('EX: _show_background_image ' +
                                      str(tries) + ' ' + str(ex))
                                time.sleep(1)
                                tries += 1
                        if bg_binary:
                            if ext == 'jpg':
                                ext = 'jpeg'
                            self._set_headers_etag(bg_filename,
                                                   'image/' + ext,
                                                   bg_binary, None,
                                                   self.server.domain_full,
                                                   False, None)
                            self._write(bg_binary)
                            fitness_performance(getreq_start_time,
                                                self.server.fitness,
                                                '_GET',
                                                '_show_background_image',
                                                self.server.debug)
                            return True
        self._404()
        return True

    def _show_default_profile_background(self, calling_domain: str, path: str,
                                         base_dir: str, theme_name: str,
                                         getreq_start_time) -> bool:
        """If a background image is missing after searching for a handle
        then substitute this image
        """
        image_extensions = get_image_extensions()
        for ext in image_extensions:
            bg_filename = \
                base_dir + '/theme/' + theme_name + '/image.' + ext
            if os.path.isfile(bg_filename):
                if self._etag_exists(bg_filename):
                    # The file has not changed
                    self._304()
                    return True

                tries = 0
                bg_binary = None
                while tries < 5:
                    try:
                        with open(bg_filename, 'rb') as av_file:
                            bg_binary = av_file.read()
                            break
                    except BaseException as ex:
                        print('EX: _show_default_profile_background ' +
                              str(tries) + ' ' + str(ex))
                        time.sleep(1)
                        tries += 1
                if bg_binary:
                    if ext == 'jpg':
                        ext = 'jpeg'
                    self._set_headers_etag(bg_filename,
                                           'image/' + ext,
                                           bg_binary, None,
                                           self.server.domain_full,
                                           False, None)
                    self._write(bg_binary)
                    fitness_performance(getreq_start_time,
                                        self.server.fitness,
                                        '_GET',
                                        '_show_default_profile_background',
                                        self.server.debug)
                    return True
                break

        self._404()
        return True

    def _show_share_image(self, calling_domain: str, path: str,
                          base_dir: str, getreq_start_time) -> bool:
        """Show a shared item image
        """
        if not is_image_file(path):
            self._404()
            return True

        media_str = path.split('/sharefiles/')[1]
        media_filename = base_dir + '/sharefiles/' + media_str
        if not os.path.isfile(media_filename):
            self._404()
            return True

        if self._etag_exists(media_filename):
            # The file has not changed
            self._304()
            return True

        media_file_type = get_image_mime_type(media_filename)
        media_binary = None
        try:
            with open(media_filename, 'rb') as av_file:
                media_binary = av_file.read()
        except OSError:
            print('EX: unable to read binary ' + media_filename)
        if media_binary:
            self._set_headers_etag(media_filename,
                                   media_file_type,
                                   media_binary, None,
                                   self.server.domain_full,
                                   False, None)
            self._write(media_binary)
        fitness_performance(getreq_start_time,
                            self.server.fitness,
                            '_GET', '_show_share_image',
                            self.server.debug)
        return True

    def _show_avatar_or_banner(self, referer_domain: str, path: str,
                               base_dir: str, domain: str,
                               getreq_start_time) -> bool:
        """Shows an avatar or banner or profile background image
        """
        if '/users/' not in path:
            if '/system/accounts/avatars/' not in path and \
               '/system/accounts/headers/' not in path and \
               '/accounts/avatars/' not in path and \
               '/accounts/headers/' not in path:
                return False
        if not is_image_file(path):
            return False
        if '/system/accounts/avatars/' in path:
            avatar_str = path.split('/system/accounts/avatars/')[1]
        elif '/accounts/avatars/' in path:
            avatar_str = path.split('/accounts/avatars/')[1]
        elif '/system/accounts/headers/' in path:
            avatar_str = path.split('/system/accounts/headers/')[1]
        elif '/accounts/headers/' in path:
            avatar_str = path.split('/accounts/headers/')[1]
        else:
            avatar_str = path.split('/users/')[1]
        if not ('/' in avatar_str and '.temp.' not in path):
            return False
        avatar_nickname = avatar_str.split('/')[0]
        avatar_file = avatar_str.split('/')[1]
        avatar_file_ext = avatar_file.split('.')[-1]
        # remove any numbers, eg. avatar123.png becomes avatar.png
        if avatar_file.startswith('avatar'):
            avatar_file = 'avatar.' + avatar_file_ext
        elif avatar_file.startswith('banner'):
            avatar_file = 'banner.' + avatar_file_ext
        elif avatar_file.startswith('search_banner'):
            avatar_file = 'search_banner.' + avatar_file_ext
        elif avatar_file.startswith('image'):
            avatar_file = 'image.' + avatar_file_ext
        elif avatar_file.startswith('left_col_image'):
            avatar_file = 'left_col_image.' + avatar_file_ext
        elif avatar_file.startswith('right_col_image'):
            avatar_file = 'right_col_image.' + avatar_file_ext
        avatar_filename = \
            acct_dir(base_dir, avatar_nickname, domain) + '/' + avatar_file
        if not os.path.isfile(avatar_filename):
            original_ext = avatar_file_ext
            original_avatar_file = avatar_file
            alt_ext = get_image_extensions()
            alt_found = False
            for alt in alt_ext:
                if alt == original_ext:
                    continue
                avatar_file = \
                    original_avatar_file.replace('.' + original_ext,
                                                 '.' + alt)
                avatar_filename = \
                    acct_dir(base_dir, avatar_nickname, domain) + \
                    '/' + avatar_file
                if os.path.isfile(avatar_filename):
                    alt_found = True
                    break
            if not alt_found:
                return False
        if self._etag_exists(avatar_filename):
            # The file has not changed
            self._304()
            return True

        avatar_tm = os.path.getmtime(avatar_filename)
        last_modified_time = datetime.datetime.fromtimestamp(avatar_tm)
        last_modified_time_str = \
            last_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

        media_image_type = get_image_mime_type(avatar_file)
        media_binary = None
        try:
            with open(avatar_filename, 'rb') as av_file:
                media_binary = av_file.read()
        except OSError:
            print('EX: unable to read avatar ' + avatar_filename)
        if media_binary:
            self._set_headers_etag(avatar_filename, media_image_type,
                                   media_binary, None,
                                   referer_domain, True,
                                   last_modified_time_str)
            self._write(media_binary)
        fitness_performance(getreq_start_time,
                            self.server.fitness,
                            '_GET', '_show_avatar_or_banner',
                            self.server.debug)
        return True

    def _confirm_delete_event(self, calling_domain: str, path: str,
                              base_dir: str, http_prefix: str, cookie: str,
                              translate: {}, domain_full: str,
                              onion_domain: str, i2p_domain: str,
                              getreq_start_time) -> bool:
        """Confirm whether to delete a calendar event
        """
        post_id = path.split('?eventid=')[1]
        if '?' in post_id:
            post_id = post_id.split('?')[0]
        post_time = path.split('?time=')[1]
        if '?' in post_time:
            post_time = post_time.split('?')[0]
        post_year = path.split('?year=')[1]
        if '?' in post_year:
            post_year = post_year.split('?')[0]
        post_month = path.split('?month=')[1]
        if '?' in post_month:
            post_month = post_month.split('?')[0]
        post_day = path.split('?day=')[1]
        if '?' in post_day:
            post_day = post_day.split('?')[0]
        # show the confirmation screen screen
        msg = html_calendar_delete_confirm(self.server.css_cache,
                                           translate,
                                           base_dir, path,
                                           http_prefix,
                                           domain_full,
                                           post_id, post_time,
                                           post_year, post_month, post_day,
                                           calling_domain)
        if not msg:
            actor = \
                http_prefix + '://' + \
                domain_full + \
                path.split('/eventdelete')[0]
            if calling_domain.endswith('.onion') and onion_domain:
                actor = \
                    'http://' + onion_domain + \
                    path.split('/eventdelete')[0]
            elif calling_domain.endswith('.i2p') and i2p_domain:
                actor = \
                    'http://' + i2p_domain + \
                    path.split('/eventdelete')[0]
            self._redirect_headers(actor + '/calendar',
                                   cookie, calling_domain)
            fitness_performance(getreq_start_time,
                                self.server.fitness,
                                '_GET', '_confirm_delete_event',
                                self.server.debug)
            return True
        msg = msg.encode('utf-8')
        msglen = len(msg)
        self._set_headers('text/html', msglen,
                          cookie, calling_domain, False)
        self._write(msg)
        return True

    def _show_new_post(self, calling_domain: str, path: str,
                       media_instance: bool, translate: {},
                       base_dir: str, http_prefix: str,
                       in_reply_to_url: str, reply_to_list: [],
                       share_description: str, reply_page_number: int,
                       reply_category: str,
                       domain: str, domain_full: str,
                       getreq_start_time, cookie,
                       no_drop_down: bool, conversation_id: str) -> bool:
        """Shows the new post screen
        """
        is_new_post_endpoint = False
        if '/users/' in path and '/new' in path:
            # Various types of new post in the web interface
            new_post_endpoints = get_new_post_endpoints()
            for curr_post_type in new_post_endpoints:
                if path.endswith('/' + curr_post_type):
                    is_new_post_endpoint = True
                    break
        if is_new_post_endpoint:
            nickname = get_nickname_from_actor(path)

            if in_reply_to_url:
                reply_interval_hours = self.server.default_reply_interval_hrs
                if not can_reply_to(base_dir, nickname, domain,
                                    in_reply_to_url, reply_interval_hours):
                    print('Reply outside of time window ' + in_reply_to_url +
                          str(reply_interval_hours) + ' hours')
                    self._403()
                    return True
                elif self.server.debug:
                    print('Reply is within time interval: ' +
                          str(reply_interval_hours) + ' hours')

            access_keys = self.server.access_keys
            if self.server.key_shortcuts.get(nickname):
                access_keys = self.server.key_shortcuts[nickname]

            custom_submit_text = get_config_param(base_dir, 'customSubmitText')

            post_json_object = None
            if in_reply_to_url:
                reply_post_filename = \
                    locate_post(base_dir, nickname, domain, in_reply_to_url)
                if reply_post_filename:
                    post_json_object = load_json(reply_post_filename)

            msg = html_new_post(self.server.css_cache,
                                media_instance,
                                translate,
                                base_dir,
                                http_prefix,
                                path, in_reply_to_url,
                                reply_to_list,
                                share_description, None,
                                reply_page_number,
                                reply_category,
                                nickname, domain,
                                domain_full,
                                self.server.default_timeline,
                                self.server.newswire,
                                self.server.theme_name,
                                no_drop_down, access_keys,
                                custom_submit_text,
                                conversation_id,
                                self.server.recent_posts_cache,
                                self.server.max_recent_posts,
                                self.server.session,
                                self.server.cached_webfingers,
                                self.server.person_cache,
                                self.server.port,
                                post_json_object,
                                self.server.project_version,
                                self.server.yt_replace_domain,
                                self.server.twitter_replacement_domain,
                                self.server.show_published_date_only,
                                self.server.peertube_instances,
                                self.server.allow_local_network_access,
                                self.server.system_language,
                                self.server.max_like_count,
                                self.server.signing_priv_key_pem,
                                self.server.cw_lists,
                                self.server.lists_enabled,
                                self.server.default_timeline).encode('utf-8')
            if not msg:
                print('Error replying to ' + in_reply_to_url)
                self._404()
                return True
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time,
                                self.server.fitness,
                                '_GET', '_show_new_post',
                                self.server.debug)
            return True
        return False

    def _show_known_crawlers(self, calling_domain: str, path: str,
                             base_dir: str, known_crawlers: {}) -> bool:
        """Show a list of known web crawlers
        """
        if '/users/' not in path:
            return False
        if not path.endswith('/crawlers'):
            return False
        nickname = get_nickname_from_actor(path)
        if not nickname:
            return False
        if not is_moderator(base_dir, nickname):
            return False
        crawlers_list = []
        curr_time = int(time.time())
        recent_crawlers = 60 * 60 * 24 * 30
        for ua_str, item in known_crawlers.items():
            if item['lastseen'] - curr_time < recent_crawlers:
                hits_str = str(item['hits']).zfill(8)
                crawlers_list.append(hits_str + ' ' + ua_str)
        crawlers_list.sort(reverse=True)
        msg = ''
        for line_str in crawlers_list:
            msg += line_str + '\n'
        msg = msg.encode('utf-8')
        msglen = len(msg)
        self._set_headers('text/plain; charset=utf-8', msglen,
                          None, calling_domain, True)
        self._write(msg)
        return True

    def _edit_profile(self, calling_domain: str, path: str,
                      translate: {}, base_dir: str,
                      http_prefix: str, domain: str, port: int,
                      cookie: str) -> bool:
        """Show the edit profile screen
        """
        if '/users/' in path and path.endswith('/editprofile'):
            peertube_instances = self.server.peertube_instances
            nickname = get_nickname_from_actor(path)
            if nickname:
                city = get_spoofed_city(self.server.city,
                                        base_dir, nickname, domain)
            else:
                city = self.server.city

            access_keys = self.server.access_keys
            if '/users/' in path:
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]

            default_reply_interval_hrs = self.server.default_reply_interval_hrs
            msg = html_edit_profile(self.server.css_cache,
                                    translate,
                                    base_dir,
                                    path, domain,
                                    port,
                                    http_prefix,
                                    self.server.default_timeline,
                                    self.server.theme_name,
                                    peertube_instances,
                                    self.server.text_mode_banner,
                                    city,
                                    self.server.user_agents_blocked,
                                    access_keys,
                                    default_reply_interval_hrs,
                                    self.server.cw_lists,
                                    self.server.lists_enabled).encode('utf-8')
            if msg:
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
            else:
                self._404()
            return True
        return False

    def _edit_links(self, calling_domain: str, path: str,
                    translate: {}, base_dir: str,
                    http_prefix: str, domain: str, port: int,
                    cookie: str, theme: str) -> bool:
        """Show the links from the left column
        """
        if '/users/' in path and path.endswith('/editlinks'):
            nickname = path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]

            access_keys = self.server.access_keys
            if self.server.key_shortcuts.get(nickname):
                access_keys = self.server.key_shortcuts[nickname]

            msg = html_edit_links(self.server.css_cache,
                                  translate,
                                  base_dir,
                                  path, domain,
                                  port,
                                  http_prefix,
                                  self.server.default_timeline,
                                  theme, access_keys).encode('utf-8')
            if msg:
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
            else:
                self._404()
            return True
        return False

    def _edit_newswire(self, calling_domain: str, path: str,
                       translate: {}, base_dir: str,
                       http_prefix: str, domain: str, port: int,
                       cookie: str) -> bool:
        """Show the newswire from the right column
        """
        if '/users/' in path and path.endswith('/editnewswire'):
            nickname = path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]

            access_keys = self.server.access_keys
            if self.server.key_shortcuts.get(nickname):
                access_keys = self.server.key_shortcuts[nickname]

            msg = html_edit_newswire(self.server.css_cache,
                                     translate,
                                     base_dir,
                                     path, domain,
                                     port,
                                     http_prefix,
                                     self.server.default_timeline,
                                     self.server.theme_name,
                                     access_keys).encode('utf-8')
            if msg:
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
            else:
                self._404()
            return True
        return False

    def _edit_news_post(self, calling_domain: str, path: str,
                        translate: {}, base_dir: str,
                        http_prefix: str, domain: str, port: int,
                        domain_full: str,
                        cookie: str) -> bool:
        """Show the edit screen for a news post
        """
        if '/users/' in path and '/editnewspost=' in path:
            post_actor = 'news'
            if '?actor=' in path:
                post_actor = path.split('?actor=')[1]
                if '?' in post_actor:
                    post_actor = post_actor.split('?')[0]
            post_id = path.split('/editnewspost=')[1]
            if '?' in post_id:
                post_id = post_id.split('?')[0]
            post_url = \
                local_actor_url(http_prefix, post_actor, domain_full) + \
                '/statuses/' + post_id
            path = path.split('/editnewspost=')[0]
            msg = html_edit_news_post(self.server.css_cache,
                                      translate, base_dir,
                                      path, domain, port,
                                      http_prefix,
                                      post_url,
                                      self.server.system_language)
            if msg:
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
            else:
                self._404()
            return True
        return False

    def _get_following_json(self, base_dir: str, path: str,
                            calling_domain: str,
                            http_prefix: str,
                            domain: str, port: int,
                            followingItemsPerPage: int,
                            debug: bool, listName='following') -> None:
        """Returns json collection for following.txt
        """
        following_json = \
            get_following_feed(base_dir, domain, port, path, http_prefix,
                               True, followingItemsPerPage, listName)
        if not following_json:
            if debug:
                print(listName + ' json feed not found for ' + path)
            self._404()
            return
        msg = json.dumps(following_json,
                         ensure_ascii=False).encode('utf-8')
        msglen = len(msg)
        self._set_headers('application/json',
                          msglen, None, calling_domain, False)
        self._write(msg)

    def _send_block(self, http_prefix: str,
                    blocker_nickname: str, blocker_domain_full: str,
                    blocking_nickname: str, blocking_domain_full: str) -> bool:
        if blocker_domain_full == blocking_domain_full:
            if blocker_nickname == blocking_nickname:
                # don't block self
                return False
        block_actor = \
            local_actor_url(http_prefix, blocker_nickname, blocker_domain_full)
        to_url = 'https://www.w3.org/ns/activitystreams#Public'
        cc_url = block_actor + '/followers'

        blocked_url = \
            http_prefix + '://' + blocking_domain_full + \
            '/@' + blocking_nickname
        block_json = {
            "@context": "https://www.w3.org/ns/activitystreams",
            'type': 'Block',
            'actor': block_actor,
            'object': blocked_url,
            'to': [to_url],
            'cc': [cc_url]
        }
        self._post_to_outbox(block_json, self.server.project_version,
                             blocker_nickname)
        return True

    def _get_referer_domain(self, ua_str: str) -> str:
        """Returns the referer domain
        Which domain is the GET request coming from?
        """
        referer_domain = None
        if self.headers.get('referer'):
            referer_domain = \
                user_agent_domain(self.headers['referer'], self.server.debug)
        elif self.headers.get('Referer'):
            referer_domain = \
                user_agent_domain(self.headers['Referer'], self.server.debug)
        elif self.headers.get('Signature'):
            if 'keyId="' in self.headers['Signature']:
                referer_domain = self.headers['Signature'].split('keyId="')[1]
                if '/' in referer_domain:
                    referer_domain = referer_domain.split('/')[0]
                elif '#' in referer_domain:
                    referer_domain = referer_domain.split('#')[0]
                elif '"' in referer_domain:
                    referer_domain = referer_domain.split('"')[0]
        elif ua_str:
            referer_domain = user_agent_domain(ua_str, self.server.debug)
        return referer_domain

    def _get_user_agent(self) -> str:
        """Returns the user agent string from the headers
        """
        ua_str = None
        if self.headers.get('User-Agent'):
            ua_str = self.headers['User-Agent']
        elif self.headers.get('user-agent'):
            ua_str = self.headers['user-agent']
        elif self.headers.get('User-agent'):
            ua_str = self.headers['User-agent']
        return ua_str

    def _permitted_crawler_path(self, path: str) -> bool:
        """Is the given path permitted to be crawled by a search engine?
        this should only allow through basic information, such as nodeinfo
        """
        if path == '/' or path == '/about' or path == '/login' or \
           path.startswith('/blog/'):
            return True
        return False

    def do_GET(self):
        calling_domain = self.server.domain_full

        if self.headers.get('Host'):
            calling_domain = decoded_host(self.headers['Host'])
            if self.server.onion_domain:
                if calling_domain not in (self.server.domain,
                                          self.server.domain_full,
                                          self.server.onion_domain):
                    print('GET domain blocked: ' + calling_domain)
                    self._400()
                    return
            elif self.server.i2p_domain:
                if calling_domain not in (self.server.domain,
                                          self.server.domain_full,
                                          self.server.i2p_domain):
                    print('GET domain blocked: ' + calling_domain)
                    self._400()
                    return
            else:
                if calling_domain not in (self.server.domain,
                                          self.server.domain_full):
                    print('GET domain blocked: ' + calling_domain)
                    self._400()
                    return

        ua_str = self._get_user_agent()

        if not self._permitted_crawler_path(self.path):
            if self._blocked_user_agent(calling_domain, ua_str):
                self._400()
                return

        referer_domain = self._get_referer_domain(ua_str)

        getreq_start_time = time.time()

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'start', self.server.debug)

        # Since fediverse crawlers are quite active,
        # make returning info to them high priority
        # get nodeinfo endpoint
        if self._nodeinfo(ua_str, calling_domain, referer_domain,
                          self.server.http_prefix, 5, self.server.debug):
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_nodeinfo[calling_domain]',
                            self.server.debug)

        if self.path == '/logout':
            if not self.server.news_instance:
                msg = \
                    html_login(self.server.css_cache,
                               self.server.translate,
                               self.server.base_dir,
                               self.server.http_prefix,
                               self.server.domain_full,
                               self.server.system_language,
                               False).encode('utf-8')
                msglen = len(msg)
                self._logout_headers('text/html', msglen, calling_domain)
                self._write(msg)
            else:
                if calling_domain.endswith('.onion') and \
                   self.server.onion_domain:
                    self._logout_redirect('http://' +
                                          self.server.onion_domain +
                                          '/users/news', None,
                                          calling_domain)
                elif (calling_domain.endswith('.i2p') and
                      self.server.i2p_domain):
                    self._logout_redirect('http://' +
                                          self.server.i2p_domain +
                                          '/users/news', None,
                                          calling_domain)
                else:
                    self._logout_redirect(self.server.http_prefix +
                                          '://' +
                                          self.server.domain_full +
                                          '/users/news',
                                          None, calling_domain)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'logout',
                                self.server.debug)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show logout',
                            self.server.debug)

        # replace https://domain/@nick with https://domain/users/nick
        if self.path.startswith('/@'):
            self.path = self.path.replace('/@', '/users/')
            # replace https://domain/@nick/statusnumber
            # with https://domain/users/nick/statuses/statusnumber
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                status_number_str = nickname.split('/')[1]
                if status_number_str.isdigit():
                    nickname = nickname.split('/')[0]
                    self.path = \
                        self.path.replace('/users/' + nickname + '/',
                                          '/users/' + nickname + '/statuses/')

        # instance actor
        if self.path == '/actor' or \
           self.path == '/users/actor' or \
           self.path == '/Actor' or \
           self.path == '/users/Actor':
            self.path = '/users/inbox'
            if self._show_instance_actor(calling_domain, self.path,
                                         self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         self.server.domain_full,
                                         self.server.port,
                                         self.server.onion_domain,
                                         self.server.i2p_domain,
                                         getreq_start_time,
                                         self.server.proxy_type,
                                         None, self.server.debug,
                                         self.server.enable_shared_inbox):
                return
            else:
                self._404()
                return

        # turn off dropdowns on new post screen
        no_drop_down = False
        if self.path.endswith('?nodropdown'):
            no_drop_down = True
            self.path = self.path.replace('?nodropdown', '')

        # redirect music to #nowplaying list
        if self.path == '/music' or self.path == '/nowplaying':
            self.path = '/tags/nowplaying'

        if self.server.debug:
            print('DEBUG: GET from ' + self.server.base_dir +
                  ' path: ' + self.path + ' busy: ' +
                  str(self.server.getreq_busy))

        if self.server.debug:
            print(str(self.headers))

        cookie = None
        if self.headers.get('Cookie'):
            cookie = self.headers['Cookie']

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'get cookie',
                            self.server.debug)

        if '/manifest.json' in self.path:
            if self._has_accept(calling_domain):
                if not self._request_http():
                    self._progressive_web_app_manifest(calling_domain,
                                                       getreq_start_time)
                    return
                else:
                    self.path = '/'

        if '/browserconfig.xml' in self.path:
            if self._has_accept(calling_domain):
                self._browser_config(calling_domain, getreq_start_time)
                return

        # default newswire favicon, for links to sites which
        # have no favicon
        if not self.path.startswith('/favicons/'):
            if 'newswire_favicon.ico' in self.path:
                self._get_favicon(calling_domain, self.server.base_dir,
                                  self.server.debug,
                                  'newswire_favicon.ico')
                return

            # favicon image
            if 'favicon.ico' in self.path:
                self._get_favicon(calling_domain, self.server.base_dir,
                                  self.server.debug,
                                  'favicon.ico')
                return

        # check authorization
        authorized = self._is_authorized()
        if self.server.debug:
            if authorized:
                print('GET Authorization granted')
            else:
                print('GET Not authorized')

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'isAuthorized',
                            self.server.debug)

        # shared items catalog for this instance
        # this is only accessible to instance members or to
        # other instances which present an authorization token
        if self.path.startswith('/catalog') or \
           (self.path.startswith('/users/') and '/catalog' in self.path):
            catalog_authorized = authorized
            if not catalog_authorized:
                if self.server.debug:
                    print('Catalog access is not authorized. ' +
                          'Checking Authorization header')
                # Check the authorization token
                if self.headers.get('Origin') and \
                   self.headers.get('Authorization'):
                    permitted_domains = \
                        self.server.shared_items_federated_domains
                    shared_item_tokens = \
                        self.server.shared_item_federation_tokens
                    if authorize_shared_items(permitted_domains,
                                              self.server.base_dir,
                                              self.headers['Origin'],
                                              calling_domain,
                                              self.headers['Authorization'],
                                              self.server.debug,
                                              shared_item_tokens):
                        catalog_authorized = True
                    elif self.server.debug:
                        print('Authorization token refused for ' +
                              'shared items federation')
                elif self.server.debug:
                    print('No Authorization header is available for ' +
                          'shared items federation')
            # show shared items catalog for federation
            if self._has_accept(calling_domain) and catalog_authorized:
                catalog_type = 'json'
                if self.path.endswith('.csv') or self._request_csv():
                    catalog_type = 'csv'
                elif self.path.endswith('.json') or not self._request_http():
                    catalog_type = 'json'
                if self.server.debug:
                    print('Preparing DFC catalog in format ' + catalog_type)

                if catalog_type == 'json':
                    # catalog as a json
                    if not self.path.startswith('/users/'):
                        if self.server.debug:
                            print('Catalog for the instance')
                        catalog_json = \
                            shares_catalog_endpoint(self.server.base_dir,
                                                    self.server.http_prefix,
                                                    self.server.domain_full,
                                                    self.path, 'shares')
                    else:
                        domain_full = self.server.domain_full
                        http_prefix = self.server.http_prefix
                        nickname = self.path.split('/users/')[1]
                        if '/' in nickname:
                            nickname = nickname.split('/')[0]
                        if self.server.debug:
                            print('Catalog for account: ' + nickname)
                        base_dir = self.server.base_dir
                        catalog_json = \
                            shares_catalog_account_endpoint(base_dir,
                                                            http_prefix,
                                                            nickname,
                                                            self.server.domain,
                                                            domain_full,
                                                            self.path,
                                                            self.server.debug,
                                                            'shares')
                    msg = json.dumps(catalog_json,
                                     ensure_ascii=False).encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json',
                                      msglen, None, calling_domain, False)
                    self._write(msg)
                    return
                elif catalog_type == 'csv':
                    # catalog as a CSV file for import into a spreadsheet
                    msg = \
                        shares_catalog_csv_endpoint(self.server.base_dir,
                                                    self.server.http_prefix,
                                                    self.server.domain_full,
                                                    self.path,
                                                    'shares').encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/csv',
                                      msglen, None, calling_domain, False)
                    self._write(msg)
                    return
                self._404()
                return
            self._400()
            return

        # wanted items catalog for this instance
        # this is only accessible to instance members or to
        # other instances which present an authorization token
        if self.path.startswith('/wantedItems') or \
           (self.path.startswith('/users/') and '/wantedItems' in self.path):
            catalog_authorized = authorized
            if not catalog_authorized:
                if self.server.debug:
                    print('Wanted catalog access is not authorized. ' +
                          'Checking Authorization header')
                # Check the authorization token
                if self.headers.get('Origin') and \
                   self.headers.get('Authorization'):
                    permitted_domains = \
                        self.server.shared_items_federated_domains
                    shared_item_tokens = \
                        self.server.shared_item_federation_tokens
                    if authorize_shared_items(permitted_domains,
                                              self.server.base_dir,
                                              self.headers['Origin'],
                                              calling_domain,
                                              self.headers['Authorization'],
                                              self.server.debug,
                                              shared_item_tokens):
                        catalog_authorized = True
                    elif self.server.debug:
                        print('Authorization token refused for ' +
                              'wanted items federation')
                elif self.server.debug:
                    print('No Authorization header is available for ' +
                          'wanted items federation')
            # show wanted items catalog for federation
            if self._has_accept(calling_domain) and catalog_authorized:
                catalog_type = 'json'
                if self.path.endswith('.csv') or self._request_csv():
                    catalog_type = 'csv'
                elif self.path.endswith('.json') or not self._request_http():
                    catalog_type = 'json'
                if self.server.debug:
                    print('Preparing DFC wanted catalog in format ' +
                          catalog_type)

                if catalog_type == 'json':
                    # catalog as a json
                    if not self.path.startswith('/users/'):
                        if self.server.debug:
                            print('Wanted catalog for the instance')
                        catalog_json = \
                            shares_catalog_endpoint(self.server.base_dir,
                                                    self.server.http_prefix,
                                                    self.server.domain_full,
                                                    self.path, 'wanted')
                    else:
                        domain_full = self.server.domain_full
                        http_prefix = self.server.http_prefix
                        nickname = self.path.split('/users/')[1]
                        if '/' in nickname:
                            nickname = nickname.split('/')[0]
                        if self.server.debug:
                            print('Wanted catalog for account: ' + nickname)
                        base_dir = self.server.base_dir
                        catalog_json = \
                            shares_catalog_account_endpoint(base_dir,
                                                            http_prefix,
                                                            nickname,
                                                            self.server.domain,
                                                            domain_full,
                                                            self.path,
                                                            self.server.debug,
                                                            'wanted')
                    msg = json.dumps(catalog_json,
                                     ensure_ascii=False).encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/json',
                                      msglen, None, calling_domain, False)
                    self._write(msg)
                    return
                elif catalog_type == 'csv':
                    # catalog as a CSV file for import into a spreadsheet
                    msg = \
                        shares_catalog_csv_endpoint(self.server.base_dir,
                                                    self.server.http_prefix,
                                                    self.server.domain_full,
                                                    self.path,
                                                    'wanted').encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/csv',
                                      msglen, None, calling_domain, False)
                    self._write(msg)
                    return
                self._404()
                return
            self._400()
            return

        # minimal mastodon api
        if self._masto_api(self.path, calling_domain, ua_str,
                           authorized,
                           self.server.http_prefix,
                           self.server.base_dir,
                           self.authorized_nickname,
                           self.server.domain,
                           self.server.domain_full,
                           self.server.onion_domain,
                           self.server.i2p_domain,
                           self.server.translate,
                           self.server.registration,
                           self.server.system_language,
                           self.server.project_version,
                           self.server.custom_emoji,
                           self.server.show_node_info_accounts):
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_masto_api[calling_domain]',
                            self.server.debug)

        if not self._establish_session("GET"):
            self._404()
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'session fail',
                                self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'create session',
                            self.server.debug)

        # is this a html request?
        html_getreq = False
        if self._has_accept(calling_domain):
            if self._request_http():
                html_getreq = True
        else:
            if self.headers.get('Connection'):
                # https://developer.mozilla.org/en-US/
                # docs/Web/HTTP/Protocol_upgrade_mechanism
                if self.headers.get('Upgrade'):
                    print('HTTP Connection request: ' +
                          self.headers['Upgrade'])
                else:
                    print('HTTP Connection request: ' +
                          self.headers['Connection'])
                self._200()
            else:
                print('WARN: No Accept header ' + str(self.headers))
                self._400()
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'hasAccept',
                            self.server.debug)

        # cached favicon images
        # Note that this comes before the busy flag to avoid conflicts
        if self.path.startswith('/favicons/'):
            if self.server.domain_full in self.path:
                # favicon for this instance
                self._get_favicon(calling_domain, self.server.base_dir,
                                  self.server.debug,
                                  'favicon.ico')
                return
            self._show_cached_favicon(referer_domain, self.path,
                                      self.server.base_dir,
                                      getreq_start_time)
            return

        # get css
        # Note that this comes before the busy flag to avoid conflicts
        if self.path.endswith('.css'):
            if self._get_style_sheet(calling_domain, self.path,
                                     getreq_start_time):
                return

        if authorized and '/exports/' in self.path:
            self._get_exported_theme(calling_domain, self.path,
                                     self.server.base_dir,
                                     self.server.domain_full,
                                     self.server.debug)
            return

        # get fonts
        if '/fonts/' in self.path:
            self._get_fonts(calling_domain, self.path,
                            self.server.base_dir, self.server.debug,
                            getreq_start_time)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'fonts',
                            self.server.debug)

        if self.path == '/sharedInbox' or \
           self.path == '/users/inbox' or \
           self.path == '/actor/inbox' or \
           self.path == '/users/' + self.server.domain:
            # if shared inbox is not enabled
            if not self.server.enable_shared_inbox:
                self._503()
                return

            self.path = '/inbox'

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'sharedInbox enabled',
                            self.server.debug)

        if self.path == '/categories.xml':
            self._get_hashtag_categories_feed(authorized,
                                              calling_domain, self.path,
                                              self.server.base_dir,
                                              self.server.http_prefix,
                                              self.server.domain,
                                              self.server.port,
                                              self.server.proxy_type,
                                              getreq_start_time,
                                              self.server.debug)
            return

        if self.path == '/newswire.xml':
            self._get_newswire_feed(authorized,
                                    calling_domain, self.path,
                                    self.server.base_dir,
                                    self.server.http_prefix,
                                    self.server.domain,
                                    self.server.port,
                                    self.server.proxy_type,
                                    getreq_start_time,
                                    self.server.debug)
            return

        # RSS 2.0
        if self.path.startswith('/blog/') and \
           self.path.endswith('/rss.xml'):
            if not self.path == '/blog/rss.xml':
                self._get_rss2feed(authorized,
                                   calling_domain, self.path,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain,
                                   self.server.port,
                                   self.server.proxy_type,
                                   getreq_start_time,
                                   self.server.debug)
            else:
                self._get_rss2site(authorized,
                                   calling_domain, self.path,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain_full,
                                   self.server.port,
                                   self.server.proxy_type,
                                   self.server.translate,
                                   getreq_start_time,
                                   self.server.debug)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'rss2 done',
                            self.server.debug)

        # RSS 3.0
        if self.path.startswith('/blog/') and \
           self.path.endswith('/rss.txt'):
            self._get_rss3feed(authorized,
                               calling_domain, self.path,
                               self.server.base_dir,
                               self.server.http_prefix,
                               self.server.domain,
                               self.server.port,
                               self.server.proxy_type,
                               getreq_start_time,
                               self.server.debug,
                               self.server.system_language)
            return

        users_in_path = False
        if '/users/' in self.path:
            users_in_path = True

        if authorized and not html_getreq and users_in_path:
            if '/following?page=' in self.path:
                self._get_following_json(self.server.base_dir,
                                         self.path,
                                         calling_domain,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         self.server.port,
                                         self.server.followingItemsPerPage,
                                         self.server.debug, 'following')
                return
            elif '/followers?page=' in self.path:
                self._get_following_json(self.server.base_dir,
                                         self.path,
                                         calling_domain,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         self.server.port,
                                         self.server.followingItemsPerPage,
                                         self.server.debug, 'followers')
                return
            elif '/followrequests?page=' in self.path:
                self._get_following_json(self.server.base_dir,
                                         self.path,
                                         calling_domain,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         self.server.port,
                                         self.server.followingItemsPerPage,
                                         self.server.debug,
                                         'followrequests')
                return

        # authorized endpoint used for TTS of posts
        # arriving in your inbox
        if authorized and users_in_path and \
           self.path.endswith('/speaker'):
            if 'application/ssml' not in self.headers['Accept']:
                # json endpoint
                self._get_speaker(calling_domain, self.path,
                                  self.server.base_dir,
                                  self.server.domain,
                                  self.server.debug)
            else:
                xml_str = \
                    get_ssm_lbox(self.server.base_dir,
                                 self.path, self.server.domain,
                                 self.server.system_language,
                                 self.server.instanceTitle,
                                 'inbox')
                if xml_str:
                    msg = xml_str.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('application/xrd+xml', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
            return

        # show a podcast episode
        if authorized and users_in_path and html_getreq and \
           '?podepisode=' in self.path:
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            episode_timestamp = self.path.split('?podepisode=')[1].strip()
            episode_timestamp = episode_timestamp.replace('__', ' ')
            episode_timestamp = episode_timestamp.replace('aa', ':')
            if self.server.newswire.get(episode_timestamp):
                pod_episode = self.server.newswire[episode_timestamp]
                html_str = \
                    html_podcast_episode(self.server.css_cache,
                                         self.server.translate,
                                         self.server.base_dir,
                                         nickname,
                                         self.server.domain,
                                         pod_episode,
                                         self.server.theme_name,
                                         self.server.default_timeline,
                                         self.server.text_mode_banner,
                                         self.server.access_keys)
                if html_str:
                    msg = html_str.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      None, calling_domain, False)
                    self._write(msg)
                    return

        # redirect to the welcome screen
        if html_getreq and authorized and users_in_path and \
           '/welcome' not in self.path:
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            if '?' in nickname:
                nickname = nickname.split('?')[0]
            if nickname == self.authorized_nickname and \
               self.path != '/users/' + nickname:
                if not is_welcome_screen_complete(self.server.base_dir,
                                                  nickname,
                                                  self.server.domain):
                    self._redirect_headers('/users/' + nickname + '/welcome',
                                           cookie, calling_domain)
                    return

        if not html_getreq and \
           users_in_path and self.path.endswith('/pinned'):
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            pinned_post_json = \
                get_pinned_post_as_json(self.server.base_dir,
                                        self.server.http_prefix,
                                        nickname, self.server.domain,
                                        self.server.domain_full,
                                        self.server.system_language)
            message_json = {}
            if pinned_post_json:
                post_id = remove_id_ending(pinned_post_json['id'])
                message_json = \
                    outbox_message_create_wrap(self.server.http_prefix,
                                               nickname,
                                               self.server.domain,
                                               self.server.port,
                                               pinned_post_json)
                message_json['id'] = post_id + '/activity'
                message_json['object']['id'] = post_id
                message_json['object']['url'] = replace_users_with_at(post_id)
                message_json['object']['atomUri'] = post_id
            msg = json.dumps(message_json,
                             ensure_ascii=False).encode('utf-8')
            msglen = len(msg)
            self._set_headers('application/json',
                              msglen, None, calling_domain, False)
            self._write(msg)
            return

        if not html_getreq and \
           users_in_path and self.path.endswith('/collections/featured'):
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            # return the featured posts collection
            self._get_featured_collection(calling_domain,
                                          self.server.base_dir,
                                          self.path,
                                          self.server.http_prefix,
                                          nickname, self.server.domain,
                                          self.server.domain_full,
                                          self.server.system_language)
            return

        if not html_getreq and \
           users_in_path and self.path.endswith('/collections/featuredTags'):
            self._get_featured_tags_collection(calling_domain,
                                               self.path,
                                               self.server.http_prefix,
                                               self.server.domain_full)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', '_get_featured_tags_collection done',
                            self.server.debug)

        # show a performance graph
        if authorized and '/performance?graph=' in self.path:
            graph = self.path.split('?graph=')[1]
            if html_getreq and not graph.endswith('.json'):
                if graph == 'post':
                    graph = '_POST'
                elif graph == 'get':
                    graph = '_GET'
                msg = \
                    html_watch_points_graph(self.server.base_dir,
                                            self.server.fitness,
                                            graph, 16).encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'graph',
                                    self.server.debug)
                return
            else:
                graph = graph.replace('.json', '')
                if graph == 'post':
                    graph = '_POST'
                elif graph == 'get':
                    graph = '_GET'
                watch_points_json = \
                    sorted_watch_points(self.server.fitness, graph)
                msg = json.dumps(watch_points_json,
                                 ensure_ascii=False).encode('utf-8')
                msglen = len(msg)
                self._set_headers('application/json', msglen,
                                  None, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'graph json',
                                    self.server.debug)
                return

        # show the main blog page
        if html_getreq and (self.path == '/blog' or
                            self.path == '/blog/' or
                            self.path == '/blogs' or
                            self.path == '/blogs/'):
            if '/rss.xml' not in self.path:
                if not self._establish_session("show the main blog page"):
                    self._404()
                    return
                msg = html_blog_view(authorized,
                                     self.server.session,
                                     self.server.base_dir,
                                     self.server.http_prefix,
                                     self.server.translate,
                                     self.server.domain,
                                     self.server.port,
                                     MAX_POSTS_IN_BLOGS_FEED,
                                     self.server.peertube_instances,
                                     self.server.system_language,
                                     self.server.person_cache,
                                     self.server.debug)
                if msg is not None:
                    msg = msg.encode('utf-8')
                    msglen = len(msg)
                    self._set_headers('text/html', msglen,
                                      cookie, calling_domain, False)
                    self._write(msg)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', 'blog view',
                                        self.server.debug)
                    return
                self._404()
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'blog view done',
                            self.server.debug)

        # show a particular page of blog entries
        # for a particular account
        if html_getreq and self.path.startswith('/blog/'):
            if '/rss.xml' not in self.path:
                if self._show_blog_page(authorized,
                                        calling_domain, self.path,
                                        self.server.base_dir,
                                        self.server.http_prefix,
                                        self.server.domain,
                                        self.server.domain_full,
                                        self.server.port,
                                        self.server.onion_domain,
                                        self.server.i2p_domain,
                                        getreq_start_time,
                                        self.server.proxy_type,
                                        cookie, self.server.translate,
                                        self.server.debug):
                    return

        # list of registered devices for e2ee
        # see https://github.com/tootsuite/mastodon/pull/13820
        if authorized and users_in_path:
            if self.path.endswith('/collections/devices'):
                nickname = self.path.split('/users/')
                if '/' in nickname:
                    nickname = nickname.split('/')[0]
                dev_json = e2e_edevices_collection(self.server.base_dir,
                                                   nickname,
                                                   self.server.domain,
                                                   self.server.domain_full,
                                                   self.server.http_prefix)
                msg = json.dumps(dev_json,
                                 ensure_ascii=False).encode('utf-8')
                msglen = len(msg)
                self._set_headers('application/json',
                                  msglen,
                                  None, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'registered devices',
                                    self.server.debug)
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'registered devices done',
                            self.server.debug)

        if html_getreq and users_in_path:
            # show the person options screen with view/follow/block/report
            if '?options=' in self.path:
                self._show_person_options(calling_domain, self.path,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          getreq_start_time,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          cookie, self.server.debug,
                                          authorized)
                return

            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'person options done',
                                self.server.debug)
            # show blog post
            blog_filename, nickname = \
                path_contains_blog_link(self.server.base_dir,
                                        self.server.http_prefix,
                                        self.server.domain,
                                        self.server.domain_full,
                                        self.path)
            if blog_filename and nickname:
                post_json_object = load_json(blog_filename)
                if is_blog_post(post_json_object):
                    msg = html_blog_post(self.server.session,
                                         authorized,
                                         self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.translate,
                                         nickname, self.server.domain,
                                         self.server.domain_full,
                                         post_json_object,
                                         self.server.peertube_instances,
                                         self.server.system_language,
                                         self.server.person_cache,
                                         self.server.debug,
                                         self.server.content_license_url)
                    if msg is not None:
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('text/html', msglen,
                                          cookie, calling_domain, False)
                        self._write(msg)
                        fitness_performance(getreq_start_time,
                                            self.server.fitness,
                                            '_GET', 'blog post 2',
                                            self.server.debug)
                        return
                    self._404()
                    return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'blog post 2 done',
                            self.server.debug)

        # after selecting a shared item from the left column then show it
        if html_getreq and \
           '?showshare=' in self.path and '/users/' in self.path:
            item_id = self.path.split('?showshare=')[1]
            if '?' in item_id:
                item_id = item_id.split('?')[0]
            category = ''
            if '?category=' in self.path:
                category = self.path.split('?category=')[1]
            if '?' in category:
                category = category.split('?')[0]
            users_path = self.path.split('?showshare=')[0]
            nickname = users_path.replace('/users/', '')
            item_id = urllib.parse.unquote_plus(item_id.strip())
            msg = \
                html_show_share(self.server.base_dir,
                                self.server.domain, nickname,
                                self.server.http_prefix,
                                self.server.domain_full,
                                item_id, self.server.translate,
                                self.server.shared_items_federated_domains,
                                self.server.default_timeline,
                                self.server.theme_name, 'shares', category)
            if not msg:
                if calling_domain.endswith('.onion') and \
                   self.server.onion_domain:
                    actor = 'http://' + self.server.onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and
                      self.server.i2p_domain):
                    actor = 'http://' + self.server.i2p_domain + users_path
                self._redirect_headers(actor + '/tlshares',
                                       cookie, calling_domain)
                return
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'html_show_share',
                                self.server.debug)
            return

        # after selecting a wanted item from the left column then show it
        if html_getreq and \
           '?showwanted=' in self.path and '/users/' in self.path:
            item_id = self.path.split('?showwanted=')[1]
            if ';' in item_id:
                item_id = item_id.split(';')[0]
            category = self.path.split('?category=')[1]
            if ';' in category:
                category = category.split(';')[0]
            users_path = self.path.split('?showwanted=')[0]
            nickname = users_path.replace('/users/', '')
            item_id = urllib.parse.unquote_plus(item_id.strip())
            msg = \
                html_show_share(self.server.base_dir,
                                self.server.domain, nickname,
                                self.server.http_prefix,
                                self.server.domain_full,
                                item_id, self.server.translate,
                                self.server.shared_items_federated_domains,
                                self.server.default_timeline,
                                self.server.theme_name, 'wanted', category)
            if not msg:
                if calling_domain.endswith('.onion') and \
                   self.server.onion_domain:
                    actor = 'http://' + self.server.onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and
                      self.server.i2p_domain):
                    actor = 'http://' + self.server.i2p_domain + users_path
                self._redirect_headers(actor + '/tlwanted',
                                       cookie, calling_domain)
                return
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'htmlShowWanted',
                                self.server.debug)
            return

        # remove a shared item
        if html_getreq and '?rmshare=' in self.path:
            item_id = self.path.split('?rmshare=')[1]
            item_id = urllib.parse.unquote_plus(item_id.strip())
            users_path = self.path.split('?rmshare=')[0]
            actor = \
                self.server.http_prefix + '://' + \
                self.server.domain_full + users_path
            msg = html_confirm_remove_shared_item(self.server.css_cache,
                                                  self.server.translate,
                                                  self.server.base_dir,
                                                  actor, item_id,
                                                  calling_domain, 'shares')
            if not msg:
                if calling_domain.endswith('.onion') and \
                   self.server.onion_domain:
                    actor = 'http://' + self.server.onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and
                      self.server.i2p_domain):
                    actor = 'http://' + self.server.i2p_domain + users_path
                self._redirect_headers(actor + '/tlshares',
                                       cookie, calling_domain)
                return
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'remove shared item',
                                self.server.debug)
            return

        # remove a wanted item
        if html_getreq and '?rmwanted=' in self.path:
            item_id = self.path.split('?rmwanted=')[1]
            item_id = urllib.parse.unquote_plus(item_id.strip())
            users_path = self.path.split('?rmwanted=')[0]
            actor = \
                self.server.http_prefix + '://' + \
                self.server.domain_full + users_path
            msg = html_confirm_remove_shared_item(self.server.css_cache,
                                                  self.server.translate,
                                                  self.server.base_dir,
                                                  actor, item_id,
                                                  calling_domain, 'wanted')
            if not msg:
                if calling_domain.endswith('.onion') and \
                   self.server.onion_domain:
                    actor = 'http://' + self.server.onion_domain + users_path
                elif (calling_domain.endswith('.i2p') and
                      self.server.i2p_domain):
                    actor = 'http://' + self.server.i2p_domain + users_path
                self._redirect_headers(actor + '/tlwanted',
                                       cookie, calling_domain)
                return
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._set_headers('text/html', msglen,
                              cookie, calling_domain, False)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'remove shared item',
                                self.server.debug)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'remove shared item done',
                            self.server.debug)

        if self.path.startswith('/terms'):
            if calling_domain.endswith('.onion') and \
               self.server.onion_domain:
                msg = html_terms_of_service(self.server.css_cache,
                                            self.server.base_dir, 'http',
                                            self.server.onion_domain)
            elif (calling_domain.endswith('.i2p') and
                  self.server.i2p_domain):
                msg = html_terms_of_service(self.server.css_cache,
                                            self.server.base_dir, 'http',
                                            self.server.i2p_domain)
            else:
                msg = html_terms_of_service(self.server.css_cache,
                                            self.server.base_dir,
                                            self.server.http_prefix,
                                            self.server.domain_full)
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html', msglen, calling_domain)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'terms of service shown',
                                self.server.debug)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'terms of service done',
                            self.server.debug)

        # show a list of who you are following
        if html_getreq and authorized and users_in_path and \
           self.path.endswith('/followingaccounts'):
            nickname = get_nickname_from_actor(self.path)
            following_filename = \
                acct_dir(self.server.base_dir,
                         nickname, self.server.domain) + '/following.txt'
            if not os.path.isfile(following_filename):
                self._404()
                return
            msg = html_following_list(self.server.css_cache,
                                      self.server.base_dir, following_filename)
            msglen = len(msg)
            self._login_headers('text/html', msglen, calling_domain)
            self._write(msg.encode('utf-8'))
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'following accounts shown',
                                self.server.debug)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'following accounts done',
                            self.server.debug)

        if self.path.endswith('/about'):
            if calling_domain.endswith('.onion'):
                msg = \
                    html_about(self.server.css_cache,
                               self.server.base_dir, 'http',
                               self.server.onion_domain,
                               None, self.server.translate,
                               self.server.system_language)
            elif calling_domain.endswith('.i2p'):
                msg = \
                    html_about(self.server.css_cache,
                               self.server.base_dir, 'http',
                               self.server.i2p_domain,
                               None, self.server.translate,
                               self.server.system_language)
            else:
                msg = \
                    html_about(self.server.css_cache,
                               self.server.base_dir,
                               self.server.http_prefix,
                               self.server.domain_full,
                               self.server.onion_domain,
                               self.server.translate,
                               self.server.system_language)
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html', msglen, calling_domain)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'show about screen',
                                self.server.debug)
            return

        if html_getreq and users_in_path and authorized and \
           self.path.endswith('/accesskeys'):
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]

            access_keys = self.server.access_keys
            if self.server.key_shortcuts.get(nickname):
                access_keys = \
                    self.server.key_shortcuts[nickname]

            msg = \
                html_access_keys(self.server.css_cache,
                                 self.server.base_dir,
                                 nickname, self.server.domain,
                                 self.server.translate,
                                 access_keys,
                                 self.server.access_keys,
                                 self.server.default_timeline)
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html', msglen, calling_domain)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'show accesskeys screen',
                                self.server.debug)
            return

        if html_getreq and users_in_path and authorized and \
           self.path.endswith('/themedesigner'):
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]

            if not is_artist(self.server.base_dir, nickname):
                self._403()
                return

            msg = \
                html_theme_designer(self.server.css_cache,
                                    self.server.base_dir,
                                    nickname, self.server.domain,
                                    self.server.translate,
                                    self.server.default_timeline,
                                    self.server.theme_name,
                                    self.server.access_keys)
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html', msglen, calling_domain)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'show theme designer screen',
                                self.server.debug)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show about screen done',
                            self.server.debug)

        # the initial welcome screen after first logging in
        if html_getreq and authorized and \
           '/users/' in self.path and self.path.endswith('/welcome'):
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            if not is_welcome_screen_complete(self.server.base_dir,
                                              nickname,
                                              self.server.domain):
                msg = \
                    html_welcome_screen(self.server.base_dir, nickname,
                                        self.server.system_language,
                                        self.server.translate,
                                        self.server.theme_name)
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._login_headers('text/html', msglen, calling_domain)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'show welcome screen',
                                    self.server.debug)
                return
            else:
                self.path = self.path.replace('/welcome', '')

        # the welcome screen which allows you to set an avatar image
        if html_getreq and authorized and \
           '/users/' in self.path and self.path.endswith('/welcome_profile'):
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            if not is_welcome_screen_complete(self.server.base_dir,
                                              nickname,
                                              self.server.domain):
                msg = \
                    html_welcome_profile(self.server.base_dir, nickname,
                                         self.server.domain,
                                         self.server.http_prefix,
                                         self.server.domain_full,
                                         self.server.system_language,
                                         self.server.translate,
                                         self.server.theme_name)
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._login_headers('text/html', msglen, calling_domain)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'show welcome profile screen',
                                    self.server.debug)
                return
            else:
                self.path = self.path.replace('/welcome_profile', '')

        # the final welcome screen
        if html_getreq and authorized and \
           '/users/' in self.path and self.path.endswith('/welcome_final'):
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            if not is_welcome_screen_complete(self.server.base_dir,
                                              nickname,
                                              self.server.domain):
                msg = \
                    html_welcome_final(self.server.base_dir, nickname,
                                       self.server.domain,
                                       self.server.http_prefix,
                                       self.server.domain_full,
                                       self.server.system_language,
                                       self.server.translate,
                                       self.server.theme_name)
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._login_headers('text/html', msglen, calling_domain)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'show welcome final screen',
                                    self.server.debug)
                return
            else:
                self.path = self.path.replace('/welcome_final', '')

        # if not authorized then show the login screen
        if html_getreq and self.path != '/login' and \
           not is_image_file(self.path) and \
           self.path != '/' and \
           self.path != '/users/news/linksmobile' and \
           self.path != '/users/news/newswiremobile':
            if self._redirect_to_login_screen(calling_domain, self.path,
                                              self.server.http_prefix,
                                              self.server.domain_full,
                                              self.server.onion_domain,
                                              self.server.i2p_domain,
                                              getreq_start_time,
                                              authorized, self.server.debug):
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show login screen done',
                            self.server.debug)

        # manifest images used to create a home screen icon
        # when selecting "add to home screen" in browsers
        # which support progressive web apps
        if self.path == '/logo72.png' or \
           self.path == '/logo96.png' or \
           self.path == '/logo128.png' or \
           self.path == '/logo144.png' or \
           self.path == '/logo150.png' or \
           self.path == '/logo192.png' or \
           self.path == '/logo256.png' or \
           self.path == '/logo512.png' or \
           self.path == '/apple-touch-icon.png':
            media_filename = \
                self.server.base_dir + '/img' + self.path
            if os.path.isfile(media_filename):
                if self._etag_exists(media_filename):
                    # The file has not changed
                    self._304()
                    return

                tries = 0
                media_binary = None
                while tries < 5:
                    try:
                        with open(media_filename, 'rb') as av_file:
                            media_binary = av_file.read()
                            break
                    except BaseException as ex:
                        print('EX: manifest logo ' +
                              str(tries) + ' ' + str(ex))
                        time.sleep(1)
                        tries += 1
                if media_binary:
                    mime_type = media_file_mime_type(media_filename)
                    self._set_headers_etag(media_filename, mime_type,
                                           media_binary, cookie,
                                           self.server.domain_full,
                                           False, None)
                    self._write(media_binary)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', 'manifest logo shown',
                                        self.server.debug)
                    return
            self._404()
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'manifest logo done',
                            self.server.debug)

        # manifest images used to show example screenshots
        # for use by app stores
        if self.path == '/screenshot1.jpg' or \
           self.path == '/screenshot2.jpg':
            screen_filename = \
                self.server.base_dir + '/img' + self.path
            if os.path.isfile(screen_filename):
                if self._etag_exists(screen_filename):
                    # The file has not changed
                    self._304()
                    return

                tries = 0
                media_binary = None
                while tries < 5:
                    try:
                        with open(screen_filename, 'rb') as av_file:
                            media_binary = av_file.read()
                            break
                    except BaseException as ex:
                        print('EX: manifest screenshot ' +
                              str(tries) + ' ' + str(ex))
                        time.sleep(1)
                        tries += 1
                if media_binary:
                    mime_type = media_file_mime_type(screen_filename)
                    self._set_headers_etag(screen_filename, mime_type,
                                           media_binary, cookie,
                                           self.server.domain_full,
                                           False, None)
                    self._write(media_binary)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', 'show screenshot',
                                        self.server.debug)
                    return
            self._404()
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show screenshot done',
                            self.server.debug)

        # image on login screen or qrcode
        if (is_image_file(self.path) and
            (self.path.startswith('/login.') or
             self.path.startswith('/qrcode.png'))):
            icon_filename = \
                self.server.base_dir + '/accounts' + self.path
            if os.path.isfile(icon_filename):
                if self._etag_exists(icon_filename):
                    # The file has not changed
                    self._304()
                    return

                tries = 0
                media_binary = None
                while tries < 5:
                    try:
                        with open(icon_filename, 'rb') as av_file:
                            media_binary = av_file.read()
                            break
                    except BaseException as ex:
                        print('EX: login screen image ' +
                              str(tries) + ' ' + str(ex))
                        time.sleep(1)
                        tries += 1
                if media_binary:
                    mime_type_str = media_file_mime_type(icon_filename)
                    self._set_headers_etag(icon_filename,
                                           mime_type_str,
                                           media_binary, cookie,
                                           self.server.domain_full,
                                           False, None)
                    self._write(media_binary)
                    fitness_performance(getreq_start_time, self.server.fitness,
                                        '_GET', 'login screen logo',
                                        self.server.debug)
                    return
            self._404()
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'login screen logo done',
                            self.server.debug)

        # QR code for account handle
        if users_in_path and \
           self.path.endswith('/qrcode.png'):
            if self._show_q_rcode(calling_domain, self.path,
                                  self.server.base_dir,
                                  self.server.domain,
                                  self.server.port,
                                  getreq_start_time):
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'account qrcode done',
                            self.server.debug)

        # search screen banner image
        if users_in_path:
            if self.path.endswith('/search_banner.png'):
                if self._search_screen_banner(calling_domain, self.path,
                                              self.server.base_dir,
                                              self.server.domain,
                                              self.server.port,
                                              getreq_start_time):
                    return

            if self.path.endswith('/left_col_image.png'):
                if self._column_image('left', calling_domain, self.path,
                                      self.server.base_dir,
                                      self.server.domain,
                                      self.server.port,
                                      getreq_start_time):
                    return

            if self.path.endswith('/right_col_image.png'):
                if self._column_image('right', calling_domain, self.path,
                                      self.server.base_dir,
                                      self.server.domain,
                                      self.server.port,
                                      getreq_start_time):
                    return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'search screen banner done',
                            self.server.debug)

        if self.path.startswith('/defaultprofilebackground'):
            self._show_default_profile_background(calling_domain, self.path,
                                                  self.server.base_dir,
                                                  self.server.theme_name,
                                                  getreq_start_time)
            return

        # show a background image on the login or person options page
        if '-background.' in self.path:
            if self._show_background_image(calling_domain, self.path,
                                           self.server.base_dir,
                                           getreq_start_time):
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'background shown done',
                            self.server.debug)

        # emoji images
        if '/emoji/' in self.path:
            self._show_emoji(calling_domain, self.path,
                             self.server.base_dir,
                             getreq_start_time)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show emoji done',
                            self.server.debug)

        # show media
        # Note that this comes before the busy flag to avoid conflicts
        # replace mastoson-style media path
        if '/system/media_attachments/files/' in self.path:
            self.path = self.path.replace('/system/media_attachments/files/',
                                          '/media/')
        if '/media/' in self.path:
            self._show_media(calling_domain,
                             self.path, self.server.base_dir,
                             getreq_start_time)
            return

        if '/ontologies/' in self.path or \
           '/data/' in self.path:
            if not has_users_path(self.path):
                self._get_ontology(calling_domain,
                                   self.path, self.server.base_dir,
                                   getreq_start_time)
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show media done',
                            self.server.debug)

        # show shared item images
        # Note that this comes before the busy flag to avoid conflicts
        if '/sharefiles/' in self.path:
            if self._show_share_image(calling_domain, self.path,
                                      self.server.base_dir,
                                      getreq_start_time):
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'share image done',
                            self.server.debug)

        # icon images
        # Note that this comes before the busy flag to avoid conflicts
        if self.path.startswith('/icons/'):
            self._show_icon(calling_domain, self.path,
                            self.server.base_dir, getreq_start_time)
            return

        # help screen images
        # Note that this comes before the busy flag to avoid conflicts
        if self.path.startswith('/helpimages/'):
            self._show_help_screen_image(calling_domain, self.path,
                                         self.server.base_dir,
                                         getreq_start_time)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'help screen image done',
                            self.server.debug)

        # cached avatar images
        # Note that this comes before the busy flag to avoid conflicts
        if self.path.startswith('/avatars/'):
            self._show_cached_avatar(referer_domain, self.path,
                                     self.server.base_dir,
                                     getreq_start_time)
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'cached avatar done',
                            self.server.debug)

        # show avatar or background image
        # Note that this comes before the busy flag to avoid conflicts
        if self._show_avatar_or_banner(referer_domain, self.path,
                                       self.server.base_dir,
                                       self.server.domain,
                                       getreq_start_time):
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'avatar or banner shown done',
                            self.server.debug)

        # This busy state helps to avoid flooding
        # Resources which are expected to be called from a web page
        # should be above this
        curr_time_getreq = int(time.time() * 1000)
        if self.server.getreq_busy:
            if curr_time_getreq - self.server.last_getreq < 500:
                if self.server.debug:
                    print('DEBUG: GET Busy')
                self.send_response(429)
                self.end_headers()
                return
        self.server.getreq_busy = True
        self.server.last_getreq = curr_time_getreq

        # returns after this point should set getreq_busy to False

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'GET busy time',
                            self.server.debug)

        if not permitted_dir(self.path):
            if self.server.debug:
                print('DEBUG: GET Not permitted')
            self._404()
            self.server.getreq_busy = False
            return

        # get webfinger endpoint for a person
        if self._webfinger(calling_domain):
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'webfinger called',
                                self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'permitted directory',
                            self.server.debug)

        # show the login screen
        if (self.path.startswith('/login') or
            (self.path == '/' and
             not authorized and
             not self.server.news_instance)):
            # request basic auth
            msg = html_login(self.server.css_cache,
                             self.server.translate,
                             self.server.base_dir,
                             self.server.http_prefix,
                             self.server.domain_full,
                             self.server.system_language,
                             True).encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html', msglen, calling_domain)
            self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'login shown',
                                self.server.debug)
            self.server.getreq_busy = False
            return

        # show the news front page
        if self.path == '/' and \
           not authorized and \
           self.server.news_instance:
            if calling_domain.endswith('.onion') and \
               self.server.onion_domain:
                self._logout_redirect('http://' +
                                      self.server.onion_domain +
                                      '/users/news', None,
                                      calling_domain)
            elif (calling_domain.endswith('.i2p') and
                  self.server.i2p_domain):
                self._logout_redirect('http://' +
                                      self.server.i2p_domain +
                                      '/users/news', None,
                                      calling_domain)
            else:
                self._logout_redirect(self.server.http_prefix +
                                      '://' +
                                      self.server.domain_full +
                                      '/users/news',
                                      None, calling_domain)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'news front page shown',
                                self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'login shown done',
                            self.server.debug)

        # the newswire screen on mobile
        if html_getreq and self.path.startswith('/users/') and \
           self.path.endswith('/newswiremobile'):
            if (authorized or
                (not authorized and
                 self.path.startswith('/users/news/') and
                 self.server.news_instance)):
                nickname = get_nickname_from_actor(self.path)
                if not nickname:
                    self._404()
                    self.server.getreq_busy = False
                    return
                timeline_path = \
                    '/users/' + nickname + '/' + self.server.default_timeline
                show_publish_as_icon = self.server.show_publish_as_icon
                rss_icon_at_top = self.server.rss_icon_at_top
                icons_as_buttons = self.server.icons_as_buttons
                default_timeline = self.server.default_timeline
                access_keys = self.server.access_keys
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]
                msg = \
                    html_newswire_mobile(self.server.css_cache,
                                         self.server.base_dir,
                                         nickname,
                                         self.server.domain,
                                         self.server.domain_full,
                                         self.server.http_prefix,
                                         self.server.translate,
                                         self.server.newswire,
                                         self.server.positive_voting,
                                         timeline_path,
                                         show_publish_as_icon,
                                         authorized,
                                         rss_icon_at_top,
                                         icons_as_buttons,
                                         default_timeline,
                                         self.server.theme_name,
                                         access_keys).encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
                self.server.getreq_busy = False
                return

        if html_getreq and self.path.startswith('/users/') and \
           self.path.endswith('/linksmobile'):
            if (authorized or
                (not authorized and
                 self.path.startswith('/users/news/') and
                 self.server.news_instance)):
                nickname = get_nickname_from_actor(self.path)
                if not nickname:
                    self._404()
                    self.server.getreq_busy = False
                    return
                access_keys = self.server.access_keys
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]
                timeline_path = \
                    '/users/' + nickname + '/' + self.server.default_timeline
                icons_as_buttons = self.server.icons_as_buttons
                default_timeline = self.server.default_timeline
                shared_items_domains = \
                    self.server.shared_items_federated_domains
                msg = \
                    html_links_mobile(self.server.css_cache,
                                      self.server.base_dir, nickname,
                                      self.server.domain_full,
                                      self.server.http_prefix,
                                      self.server.translate,
                                      timeline_path,
                                      authorized,
                                      self.server.rss_icon_at_top,
                                      icons_as_buttons,
                                      default_timeline,
                                      self.server.theme_name,
                                      access_keys,
                                      shared_items_domains).encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen, cookie, calling_domain,
                                  False)
                self._write(msg)
                self.server.getreq_busy = False
                return

        # hashtag search
        if self.path.startswith('/tags/') or \
           (authorized and '/tags/' in self.path):
            if self.path.startswith('/tags/rss2/'):
                self._hashtag_search_rss2(calling_domain,
                                          self.path, cookie,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.port,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          getreq_start_time)
                self.server.getreq_busy = False
                return
            self._hashtag_search(calling_domain,
                                 self.path, cookie,
                                 self.server.base_dir,
                                 self.server.http_prefix,
                                 self.server.domain,
                                 self.server.domain_full,
                                 self.server.port,
                                 self.server.onion_domain,
                                 self.server.i2p_domain,
                                 getreq_start_time)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'hashtag search done',
                            self.server.debug)

        # show or hide buttons in the web interface
        if html_getreq and users_in_path and \
           self.path.endswith('/minimal') and \
           authorized:
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
                not_min = not is_minimal(self.server.base_dir,
                                         self.server.domain, nickname)
                set_minimal(self.server.base_dir,
                            self.server.domain, nickname, not_min)
                if not (self.server.media_instance or
                        self.server.blogs_instance):
                    self.path = '/users/' + nickname + '/inbox'
                else:
                    if self.server.blogs_instance:
                        self.path = '/users/' + nickname + '/tlblogs'
                    elif self.server.media_instance:
                        self.path = '/users/' + nickname + '/tlmedia'
                    else:
                        self.path = '/users/' + nickname + '/tlfeatures'

        # search for a fediverse address, shared item or emoji
        # from the web interface by selecting search icon
        if html_getreq and users_in_path:
            if self.path.endswith('/search') or \
               '/search?' in self.path:
                if '?' in self.path:
                    self.path = self.path.split('?')[0]

                nickname = self.path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]

                access_keys = self.server.access_keys
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]

                # show the search screen
                msg = html_search(self.server.css_cache,
                                  self.server.translate,
                                  self.server.base_dir, self.path,
                                  self.server.domain,
                                  self.server.default_timeline,
                                  self.server.theme_name,
                                  self.server.text_mode_banner,
                                  access_keys).encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen, cookie, calling_domain,
                                  False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'search screen shown',
                                    self.server.debug)
                self.server.getreq_busy = False
                return

        # show a hashtag category from the search screen
        if html_getreq and '/category/' in self.path:
            msg = html_search_hashtag_category(self.server.css_cache,
                                               self.server.translate,
                                               self.server.base_dir, self.path,
                                               self.server.domain,
                                               self.server.theme_name)
            if msg:
                msg = msg.encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen, cookie, calling_domain,
                                  False)
                self._write(msg)
            fitness_performance(getreq_start_time, self.server.fitness,
                                '_GET', 'hashtag category screen shown',
                                self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'search screen shown done',
                            self.server.debug)

        # Show the calendar for a user
        if html_getreq and users_in_path:
            if '/calendar' in self.path:
                nickname = self.path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]

                access_keys = self.server.access_keys
                if self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.key_shortcuts[nickname]

                # show the calendar screen
                msg = html_calendar(self.server.person_cache,
                                    self.server.css_cache,
                                    self.server.translate,
                                    self.server.base_dir, self.path,
                                    self.server.http_prefix,
                                    self.server.domain_full,
                                    self.server.text_mode_banner,
                                    access_keys).encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen, cookie, calling_domain,
                                  False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'calendar shown',
                                    self.server.debug)
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'calendar shown done',
                            self.server.debug)

        # Show confirmation for deleting a calendar event
        if html_getreq and users_in_path:
            if '/eventdelete' in self.path and \
               '?time=' in self.path and \
               '?eventid=' in self.path:
                if self._confirm_delete_event(calling_domain, self.path,
                                              self.server.base_dir,
                                              self.server.http_prefix,
                                              cookie,
                                              self.server.translate,
                                              self.server.domain_full,
                                              self.server.onion_domain,
                                              self.server.i2p_domain,
                                              getreq_start_time):
                    self.server.getreq_busy = False
                    return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'calendar delete shown done',
                            self.server.debug)

        # search for emoji by name
        if html_getreq and users_in_path:
            if self.path.endswith('/searchemoji'):
                # show the search screen
                msg = \
                    html_search_emoji_text_entry(self.server.css_cache,
                                                 self.server.translate,
                                                 self.server.base_dir,
                                                 self.path).encode('utf-8')
                msglen = len(msg)
                self._set_headers('text/html', msglen,
                                  cookie, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'emoji search shown',
                                    self.server.debug)
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'emoji search shown done',
                            self.server.debug)

        repeat_private = False
        if html_getreq and '?repeatprivate=' in self.path:
            repeat_private = True
            self.path = self.path.replace('?repeatprivate=', '?repeat=')
        # announce/repeat button was pressed
        if authorized and html_getreq and '?repeat=' in self.path:
            self._announce_button(calling_domain, self.path,
                                  self.server.base_dir,
                                  cookie, self.server.proxy_type,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.port,
                                  self.server.onion_domain,
                                  self.server.i2p_domain,
                                  getreq_start_time,
                                  repeat_private,
                                  self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show announce done',
                            self.server.debug)

        if authorized and html_getreq and '?unrepeatprivate=' in self.path:
            self.path = self.path.replace('?unrepeatprivate=', '?unrepeat=')

        # undo an announce/repeat from the web interface
        if authorized and html_getreq and '?unrepeat=' in self.path:
            self._undo_announce_button(calling_domain, self.path,
                                       self.server.base_dir,
                                       cookie, self.server.proxy_type,
                                       self.server.http_prefix,
                                       self.server.domain,
                                       self.server.domain_full,
                                       self.server.port,
                                       self.server.onion_domain,
                                       self.server.i2p_domain,
                                       getreq_start_time,
                                       repeat_private,
                                       self.server.debug,
                                       self.server.recent_posts_cache)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'unannounce done',
                            self.server.debug)

        # send a newswire moderation vote from the web interface
        if authorized and '/newswirevote=' in self.path and \
           self.path.startswith('/users/'):
            self._newswire_vote(calling_domain, self.path,
                                cookie,
                                self.server.base_dir,
                                self.server.http_prefix,
                                self.server.domain,
                                self.server.domain_full,
                                self.server.port,
                                self.server.onion_domain,
                                self.server.i2p_domain,
                                getreq_start_time,
                                self.server.proxy_type,
                                self.server.debug,
                                self.server.newswire)
            self.server.getreq_busy = False
            return

        # send a newswire moderation unvote from the web interface
        if authorized and '/newswireunvote=' in self.path and \
           self.path.startswith('/users/'):
            self._newswire_unvote(calling_domain, self.path,
                                  cookie,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.port,
                                  self.server.onion_domain,
                                  self.server.i2p_domain,
                                  getreq_start_time,
                                  self.server.proxy_type,
                                  self.server.debug,
                                  self.server.newswire)
            self.server.getreq_busy = False
            return

        # send a follow request approval from the web interface
        if authorized and '/followapprove=' in self.path and \
           self.path.startswith('/users/'):
            self._follow_approve_button(calling_domain, self.path,
                                        cookie,
                                        self.server.base_dir,
                                        self.server.http_prefix,
                                        self.server.domain,
                                        self.server.domain_full,
                                        self.server.port,
                                        self.server.onion_domain,
                                        self.server.i2p_domain,
                                        getreq_start_time,
                                        self.server.proxy_type,
                                        self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'follow approve done',
                            self.server.debug)

        # deny a follow request from the web interface
        if authorized and '/followdeny=' in self.path and \
           self.path.startswith('/users/'):
            self._follow_deny_button(calling_domain, self.path,
                                     cookie,
                                     self.server.base_dir,
                                     self.server.http_prefix,
                                     self.server.domain,
                                     self.server.domain_full,
                                     self.server.port,
                                     self.server.onion_domain,
                                     self.server.i2p_domain,
                                     getreq_start_time,
                                     self.server.proxy_type,
                                     self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'follow deny done',
                            self.server.debug)

        # like from the web interface icon
        if authorized and html_getreq and '?like=' in self.path:
            self._like_button(calling_domain, self.path,
                              self.server.base_dir,
                              self.server.http_prefix,
                              self.server.domain,
                              self.server.domain_full,
                              self.server.onion_domain,
                              self.server.i2p_domain,
                              getreq_start_time,
                              self.server.proxy_type,
                              cookie,
                              self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'like button done',
                            self.server.debug)

        # undo a like from the web interface icon
        if authorized and html_getreq and '?unlike=' in self.path:
            self._undo_like_button(calling_domain, self.path,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain,
                                   self.server.domain_full,
                                   self.server.onion_domain,
                                   self.server.i2p_domain,
                                   getreq_start_time,
                                   self.server.proxy_type,
                                   cookie, self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'unlike button done',
                            self.server.debug)

        # emoji reaction from the web interface icon
        if authorized and html_getreq and \
           '?react=' in self.path and \
           '?actor=' in self.path:
            self._reaction_button(calling_domain, self.path,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.onion_domain,
                                  self.server.i2p_domain,
                                  getreq_start_time,
                                  self.server.proxy_type,
                                  cookie,
                                  self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'emoji reaction button done',
                            self.server.debug)

        # undo an emoji reaction from the web interface icon
        if authorized and html_getreq and \
           '?unreact=' in self.path and \
           '?actor=' in self.path:
            self._undo_reaction_button(calling_domain, self.path,
                                       self.server.base_dir,
                                       self.server.http_prefix,
                                       self.server.domain,
                                       self.server.domain_full,
                                       self.server.onion_domain,
                                       self.server.i2p_domain,
                                       getreq_start_time,
                                       self.server.proxy_type,
                                       cookie, self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'unreaction button done',
                            self.server.debug)

        # bookmark from the web interface icon
        if authorized and html_getreq and '?bookmark=' in self.path:
            self._bookmark_button(calling_domain, self.path,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.port,
                                  self.server.onion_domain,
                                  self.server.i2p_domain,
                                  getreq_start_time,
                                  self.server.proxy_type,
                                  cookie, self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'bookmark shown done',
                            self.server.debug)

        # emoji recation from the web interface bottom icon
        if authorized and html_getreq and '?selreact=' in self.path:
            self._reaction_picker(calling_domain, self.path,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.port,
                                  self.server.onion_domain,
                                  self.server.i2p_domain,
                                  getreq_start_time,
                                  self.server.proxy_type,
                                  cookie, self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'bookmark shown done',
                            self.server.debug)

        # undo a bookmark from the web interface icon
        if authorized and html_getreq and '?unbookmark=' in self.path:
            self._undo_bookmark_button(calling_domain, self.path,
                                       self.server.base_dir,
                                       self.server.http_prefix,
                                       self.server.domain,
                                       self.server.domain_full,
                                       self.server.port,
                                       self.server.onion_domain,
                                       self.server.i2p_domain,
                                       getreq_start_time,
                                       self.server.proxy_type, cookie,
                                       self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'unbookmark shown done',
                            self.server.debug)

        # delete button is pressed on a post
        if authorized and html_getreq and '?delete=' in self.path:
            self._delete_button(calling_domain, self.path,
                                self.server.base_dir,
                                self.server.http_prefix,
                                self.server.domain,
                                self.server.domain_full,
                                self.server.port,
                                self.server.onion_domain,
                                self.server.i2p_domain,
                                getreq_start_time,
                                self.server.proxy_type, cookie,
                                self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'delete shown done',
                            self.server.debug)

        # The mute button is pressed
        if authorized and html_getreq and '?mute=' in self.path:
            self._mute_button(calling_domain, self.path,
                              self.server.base_dir,
                              self.server.http_prefix,
                              self.server.domain,
                              self.server.domain_full,
                              self.server.port,
                              self.server.onion_domain,
                              self.server.i2p_domain,
                              getreq_start_time,
                              self.server.proxy_type, cookie,
                              self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'post muted done',
                            self.server.debug)

        # unmute a post from the web interface icon
        if authorized and html_getreq and '?unmute=' in self.path:
            self._undo_mute_button(calling_domain, self.path,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain,
                                   self.server.domain_full,
                                   self.server.port,
                                   self.server.onion_domain,
                                   self.server.i2p_domain,
                                   getreq_start_time,
                                   self.server.proxy_type, cookie,
                                   self.server.debug)
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'unmute activated done',
                            self.server.debug)

        # reply from the web interface icon
        in_reply_to_url = None
#        replyWithDM = False
        reply_to_list = []
        reply_page_number = 1
        reply_category = ''
        share_description = None
        conversation_id = None
#        replytoActor = None
        if html_getreq:
            if '?conversationId=' in self.path:
                conversation_id = self.path.split('?conversationId=')[1]
                if '?' in conversation_id:
                    conversation_id = conversation_id.split('?')[0]
            # public reply
            if '?replyto=' in self.path:
                in_reply_to_url = self.path.split('?replyto=')[1]
                if '?' in in_reply_to_url:
                    mentions_list = in_reply_to_url.split('?')
                    for m in mentions_list:
                        if m.startswith('mention='):
                            reply_handle = m.replace('mention=', '')
                            if reply_handle not in reply_to_list:
                                reply_to_list.append(reply_handle)
                        if m.startswith('page='):
                            reply_page_str = m.replace('page=', '')
                            if reply_page_str.isdigit():
                                reply_page_number = int(reply_page_str)
#                        if m.startswith('actor='):
#                            replytoActor = m.replace('actor=', '')
                    in_reply_to_url = mentions_list[0]
                self.path = self.path.split('?replyto=')[0] + '/newpost'
                if self.server.debug:
                    print('DEBUG: replyto path ' + self.path)

            # reply to followers
            if '?replyfollowers=' in self.path:
                in_reply_to_url = self.path.split('?replyfollowers=')[1]
                if '?' in in_reply_to_url:
                    mentions_list = in_reply_to_url.split('?')
                    for ment in mentions_list:
                        if ment.startswith('mention='):
                            reply_handle = ment.replace('mention=', '')
                            ment2 = ment.replace('mention=', '')
                            if ment2 not in reply_to_list:
                                reply_to_list.append(reply_handle)
                        if ment.startswith('page='):
                            reply_page_str = ment.replace('page=', '')
                            if reply_page_str.isdigit():
                                reply_page_number = int(reply_page_str)
#                        if m.startswith('actor='):
#                            replytoActor = m.replace('actor=', '')
                    in_reply_to_url = mentions_list[0]
                self.path = self.path.split('?replyfollowers=')[0] + \
                    '/newfollowers'
                if self.server.debug:
                    print('DEBUG: replyfollowers path ' + self.path)

            # replying as a direct message,
            # for moderation posts or the dm timeline
            if '?replydm=' in self.path:
                in_reply_to_url = self.path.split('?replydm=')[1]
                in_reply_to_url = urllib.parse.unquote_plus(in_reply_to_url)
                if '?' in in_reply_to_url:
                    # multiple parameters
                    mentions_list = in_reply_to_url.split('?')
                    for ment in mentions_list:
                        if ment.startswith('mention='):
                            reply_handle = ment.replace('mention=', '')
                            in_reply_to_url = reply_handle
                            if reply_handle not in reply_to_list:
                                reply_to_list.append(reply_handle)
                        elif ment.startswith('page='):
                            reply_page_str = ment.replace('page=', '')
                            if reply_page_str.isdigit():
                                reply_page_number = int(reply_page_str)
                        elif ment.startswith('category='):
                            reply_category = ment.replace('category=', '')
                        elif ment.startswith('sharedesc:'):
                            # get the title for the shared item
                            share_description = \
                                ment.replace('sharedesc:', '').strip()
                            share_description = \
                                share_description.replace('_', ' ')
                else:
                    # single parameter
                    if in_reply_to_url.startswith('mention='):
                        reply_handle = in_reply_to_url.replace('mention=', '')
                        in_reply_to_url = reply_handle
                        if reply_handle not in reply_to_list:
                            reply_to_list.append(reply_handle)
                    elif in_reply_to_url.startswith('sharedesc:'):
                        # get the title for the shared item
                        share_description = \
                            in_reply_to_url.replace('sharedesc:', '').strip()
                        share_description = \
                            share_description.replace('_', ' ')

                self.path = self.path.split('?replydm=')[0] + '/newdm'
                if self.server.debug:
                    print('DEBUG: replydm path ' + self.path)

            # Edit a blog post
            if authorized and \
               '/users/' in self.path and \
               '?editblogpost=' in self.path and \
               ';actor=' in self.path:
                message_id = self.path.split('?editblogpost=')[1]
                if ';' in message_id:
                    message_id = message_id.split(';')[0]
                actor = self.path.split(';actor=')[1]
                if ';' in actor:
                    actor = actor.split(';')[0]
                nickname = get_nickname_from_actor(self.path.split('?')[0])
                if nickname == actor:
                    post_url = \
                        local_actor_url(self.server.http_prefix, nickname,
                                        self.server.domain_full) + \
                        '/statuses/' + message_id
                    msg = html_edit_blog(self.server.media_instance,
                                         self.server.translate,
                                         self.server.base_dir,
                                         self.server.http_prefix,
                                         self.path, reply_page_number,
                                         nickname, self.server.domain,
                                         post_url,
                                         self.server.system_language)
                    if msg:
                        msg = msg.encode('utf-8')
                        msglen = len(msg)
                        self._set_headers('text/html', msglen,
                                          cookie, calling_domain, False)
                        self._write(msg)
                        self.server.getreq_busy = False
                        return

            # list of known crawlers accessing nodeinfo or masto API
            if self._show_known_crawlers(calling_domain, self.path,
                                         self.server.base_dir,
                                         self.server.known_crawlers):
                self.server.getreq_busy = False
                return

            # edit profile in web interface
            if self._edit_profile(calling_domain, self.path,
                                  self.server.translate,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.port,
                                  cookie):
                self.server.getreq_busy = False
                return

            # edit links from the left column of the timeline in web interface
            if self._edit_links(calling_domain, self.path,
                                self.server.translate,
                                self.server.base_dir,
                                self.server.http_prefix,
                                self.server.domain,
                                self.server.port,
                                cookie,
                                self.server.theme_name):
                self.server.getreq_busy = False
                return

            # edit newswire from the right column of the timeline
            if self._edit_newswire(calling_domain, self.path,
                                   self.server.translate,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain,
                                   self.server.port,
                                   cookie):
                self.server.getreq_busy = False
                return

            # edit news post
            if self._edit_news_post(calling_domain, self.path,
                                    self.server.translate,
                                    self.server.base_dir,
                                    self.server.http_prefix,
                                    self.server.domain,
                                    self.server.port,
                                    self.server.domain_full,
                                    cookie):
                self.server.getreq_busy = False
                return

            if self._show_new_post(calling_domain, self.path,
                                   self.server.media_instance,
                                   self.server.translate,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   in_reply_to_url, reply_to_list,
                                   share_description, reply_page_number,
                                   reply_category,
                                   self.server.domain,
                                   self.server.domain_full,
                                   getreq_start_time,
                                   cookie, no_drop_down, conversation_id):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'new post done',
                            self.server.debug)

        # get an individual post from the path /@nickname/statusnumber
        if self._show_individual_at_post(authorized,
                                         calling_domain, self.path,
                                         self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         self.server.domain_full,
                                         self.server.port,
                                         self.server.onion_domain,
                                         self.server.i2p_domain,
                                         getreq_start_time,
                                         self.server.proxy_type,
                                         cookie, self.server.debug):
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'individual post done',
                            self.server.debug)

        # get replies to a post /users/nickname/statuses/number/replies
        if self.path.endswith('/replies') or '/replies?page=' in self.path:
            if self._show_replies_to_post(authorized,
                                          calling_domain, self.path,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.port,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          getreq_start_time,
                                          self.server.proxy_type, cookie,
                                          self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'post replies done',
                            self.server.debug)

        # roles on profile screen
        if self.path.endswith('/roles') and users_in_path:
            if self._show_roles(authorized,
                                calling_domain, self.path,
                                self.server.base_dir,
                                self.server.http_prefix,
                                self.server.domain,
                                self.server.domain_full,
                                self.server.port,
                                self.server.onion_domain,
                                self.server.i2p_domain,
                                getreq_start_time,
                                self.server.proxy_type,
                                cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show roles done',
                            self.server.debug)

        # show skills on the profile page
        if self.path.endswith('/skills') and users_in_path:
            if self._show_skills(authorized,
                                 calling_domain, self.path,
                                 self.server.base_dir,
                                 self.server.http_prefix,
                                 self.server.domain,
                                 self.server.domain_full,
                                 self.server.port,
                                 self.server.onion_domain,
                                 self.server.i2p_domain,
                                 getreq_start_time,
                                 self.server.proxy_type,
                                 cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show skills done',
                            self.server.debug)

        if '?notifypost=' in self.path and users_in_path and authorized:
            if self._show_notify_post(authorized,
                                      calling_domain, self.path,
                                      self.server.base_dir,
                                      self.server.http_prefix,
                                      self.server.domain,
                                      self.server.domain_full,
                                      self.server.port,
                                      self.server.onion_domain,
                                      self.server.i2p_domain,
                                      getreq_start_time,
                                      self.server.proxy_type,
                                      cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        # get an individual post from the path
        # /users/nickname/statuses/number
        if '/statuses/' in self.path and users_in_path:
            if self._show_individual_post(authorized,
                                          calling_domain, self.path,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.port,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          getreq_start_time,
                                          self.server.proxy_type,
                                          cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show status done',
                            self.server.debug)

        # get the inbox timeline for a given person
        if self.path.endswith('/inbox') or '/inbox?page=' in self.path:
            if self._show_inbox(authorized,
                                calling_domain, self.path,
                                self.server.base_dir,
                                self.server.http_prefix,
                                self.server.domain,
                                self.server.domain_full,
                                self.server.port,
                                self.server.onion_domain,
                                self.server.i2p_domain,
                                getreq_start_time,
                                self.server.proxy_type,
                                cookie, self.server.debug,
                                self.server.recent_posts_cache,
                                self.server.session,
                                self.server.default_timeline,
                                self.server.max_recent_posts,
                                self.server.translate,
                                self.server.cached_webfingers,
                                self.server.person_cache,
                                self.server.allow_deletion,
                                self.server.project_version,
                                self.server.yt_replace_domain,
                                self.server.twitter_replacement_domain):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show inbox done',
                            self.server.debug)

        # get the direct messages timeline for a given person
        if self.path.endswith('/dm') or '/dm?page=' in self.path:
            if self._show_d_ms(authorized,
                               calling_domain, self.path,
                               self.server.base_dir,
                               self.server.http_prefix,
                               self.server.domain,
                               self.server.domain_full,
                               self.server.port,
                               self.server.onion_domain,
                               self.server.i2p_domain,
                               getreq_start_time,
                               self.server.proxy_type,
                               cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show dms done',
                            self.server.debug)

        # get the replies timeline for a given person
        if self.path.endswith('/tlreplies') or '/tlreplies?page=' in self.path:
            if self._show_replies(authorized,
                                  calling_domain, self.path,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.port,
                                  self.server.onion_domain,
                                  self.server.i2p_domain,
                                  getreq_start_time,
                                  self.server.proxy_type,
                                  cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show replies 2 done',
                            self.server.debug)

        # get the media timeline for a given person
        if self.path.endswith('/tlmedia') or '/tlmedia?page=' in self.path:
            if self._show_media_timeline(authorized,
                                         calling_domain, self.path,
                                         self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         self.server.domain_full,
                                         self.server.port,
                                         self.server.onion_domain,
                                         self.server.i2p_domain,
                                         getreq_start_time,
                                         self.server.proxy_type,
                                         cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show media 2 done',
                            self.server.debug)

        # get the blogs for a given person
        if self.path.endswith('/tlblogs') or '/tlblogs?page=' in self.path:
            if self._show_blogs_timeline(authorized,
                                         calling_domain, self.path,
                                         self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         self.server.domain_full,
                                         self.server.port,
                                         self.server.onion_domain,
                                         self.server.i2p_domain,
                                         getreq_start_time,
                                         self.server.proxy_type,
                                         cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show blogs 2 done',
                            self.server.debug)

        # get the news for a given person
        if self.path.endswith('/tlnews') or '/tlnews?page=' in self.path:
            if self._show_news_timeline(authorized,
                                        calling_domain, self.path,
                                        self.server.base_dir,
                                        self.server.http_prefix,
                                        self.server.domain,
                                        self.server.domain_full,
                                        self.server.port,
                                        self.server.onion_domain,
                                        self.server.i2p_domain,
                                        getreq_start_time,
                                        self.server.proxy_type,
                                        cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        # get features (local blogs) for a given person
        if self.path.endswith('/tlfeatures') or \
           '/tlfeatures?page=' in self.path:
            if self._show_features_timeline(authorized,
                                            calling_domain, self.path,
                                            self.server.base_dir,
                                            self.server.http_prefix,
                                            self.server.domain,
                                            self.server.domain_full,
                                            self.server.port,
                                            self.server.onion_domain,
                                            self.server.i2p_domain,
                                            getreq_start_time,
                                            self.server.proxy_type,
                                            cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show news 2 done',
                            self.server.debug)

        # get the shared items timeline for a given person
        if self.path.endswith('/tlshares') or '/tlshares?page=' in self.path:
            if self._show_shares_timeline(authorized,
                                          calling_domain, self.path,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.port,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          getreq_start_time,
                                          self.server.proxy_type,
                                          cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        # get the wanted items timeline for a given person
        if self.path.endswith('/tlwanted') or '/tlwanted?page=' in self.path:
            if self._show_wanted_timeline(authorized,
                                          calling_domain, self.path,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.port,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          getreq_start_time,
                                          self.server.proxy_type,
                                          cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show shares 2 done',
                            self.server.debug)

        # block a domain from html_account_info
        if authorized and users_in_path and \
           '/accountinfo?blockdomain=' in self.path and \
           '?handle=' in self.path:
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            if not is_moderator(self.server.base_dir, nickname):
                self._400()
                self.server.getreq_busy = False
                return
            block_domain = self.path.split('/accountinfo?blockdomain=')[1]
            search_handle = block_domain.split('?handle=')[1]
            search_handle = urllib.parse.unquote_plus(search_handle)
            block_domain = block_domain.split('?handle=')[0]
            block_domain = urllib.parse.unquote_plus(block_domain.strip())
            if '?' in block_domain:
                block_domain = block_domain.split('?')[0]
            add_global_block(self.server.base_dir, '*', block_domain)
            msg = \
                html_account_info(self.server.css_cache,
                                  self.server.translate,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  nickname,
                                  self.server.domain,
                                  self.server.port,
                                  search_handle,
                                  self.server.debug,
                                  self.server.system_language,
                                  self.server.signing_priv_key_pem)
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html',
                                msglen, calling_domain)
            self._write(msg)
            self.server.getreq_busy = False
            return

        # unblock a domain from html_account_info
        if authorized and users_in_path and \
           '/accountinfo?unblockdomain=' in self.path and \
           '?handle=' in self.path:
            nickname = self.path.split('/users/')[1]
            if '/' in nickname:
                nickname = nickname.split('/')[0]
            if not is_moderator(self.server.base_dir, nickname):
                self._400()
                self.server.getreq_busy = False
                return
            block_domain = self.path.split('/accountinfo?unblockdomain=')[1]
            search_handle = block_domain.split('?handle=')[1]
            search_handle = urllib.parse.unquote_plus(search_handle)
            block_domain = block_domain.split('?handle=')[0]
            block_domain = urllib.parse.unquote_plus(block_domain.strip())
            remove_global_block(self.server.base_dir, '*', block_domain)
            msg = \
                html_account_info(self.server.css_cache,
                                  self.server.translate,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  nickname,
                                  self.server.domain,
                                  self.server.port,
                                  search_handle,
                                  self.server.debug,
                                  self.server.system_language,
                                  self.server.signing_priv_key_pem)
            msg = msg.encode('utf-8')
            msglen = len(msg)
            self._login_headers('text/html',
                                msglen, calling_domain)
            self._write(msg)
            self.server.getreq_busy = False
            return

        # get the bookmarks timeline for a given person
        if self.path.endswith('/tlbookmarks') or \
           '/tlbookmarks?page=' in self.path or \
           self.path.endswith('/bookmarks') or \
           '/bookmarks?page=' in self.path:
            if self._show_bookmarks_timeline(authorized,
                                             calling_domain, self.path,
                                             self.server.base_dir,
                                             self.server.http_prefix,
                                             self.server.domain,
                                             self.server.domain_full,
                                             self.server.port,
                                             self.server.onion_domain,
                                             self.server.i2p_domain,
                                             getreq_start_time,
                                             self.server.proxy_type,
                                             cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show bookmarks 2 done',
                            self.server.debug)

        # outbox timeline
        if self.path.endswith('/outbox') or \
           '/outbox?page=' in self.path:
            if self._show_outbox_timeline(authorized,
                                          calling_domain, self.path,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.port,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          getreq_start_time,
                                          self.server.proxy_type,
                                          cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show outbox done',
                            self.server.debug)

        # get the moderation feed for a moderator
        if self.path.endswith('/moderation') or \
           '/moderation?' in self.path:
            if self._show_mod_timeline(authorized,
                                       calling_domain, self.path,
                                       self.server.base_dir,
                                       self.server.http_prefix,
                                       self.server.domain,
                                       self.server.domain_full,
                                       self.server.port,
                                       self.server.onion_domain,
                                       self.server.i2p_domain,
                                       getreq_start_time,
                                       self.server.proxy_type,
                                       cookie, self.server.debug):
                self.server.getreq_busy = False
                return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show moderation done',
                            self.server.debug)

        if self._show_shares_feed(authorized,
                                  calling_domain, self.path,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.port,
                                  self.server.onion_domain,
                                  self.server.i2p_domain,
                                  getreq_start_time,
                                  self.server.proxy_type,
                                  cookie, self.server.debug, 'shares'):
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show profile 2 done',
                            self.server.debug)

        if self._show_following_feed(authorized,
                                     calling_domain, self.path,
                                     self.server.base_dir,
                                     self.server.http_prefix,
                                     self.server.domain,
                                     self.server.domain_full,
                                     self.server.port,
                                     self.server.onion_domain,
                                     self.server.i2p_domain,
                                     getreq_start_time,
                                     self.server.proxy_type,
                                     cookie, self.server.debug):
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show profile 3 done',
                            self.server.debug)

        if self._show_followers_feed(authorized,
                                     calling_domain, self.path,
                                     self.server.base_dir,
                                     self.server.http_prefix,
                                     self.server.domain,
                                     self.server.domain_full,
                                     self.server.port,
                                     self.server.onion_domain,
                                     self.server.i2p_domain,
                                     getreq_start_time,
                                     self.server.proxy_type,
                                     cookie, self.server.debug):
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show profile 4 done',
                            self.server.debug)

        # look up a person
        if self._show_person_profile(authorized,
                                     calling_domain, self.path,
                                     self.server.base_dir,
                                     self.server.http_prefix,
                                     self.server.domain,
                                     self.server.domain_full,
                                     self.server.port,
                                     self.server.onion_domain,
                                     self.server.i2p_domain,
                                     getreq_start_time,
                                     self.server.proxy_type,
                                     cookie, self.server.debug):
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'show profile posts done',
                            self.server.debug)

        # check that a json file was requested
        if not self.path.endswith('.json'):
            if self.server.debug:
                print('DEBUG: GET Not json: ' + self.path +
                      ' ' + self.server.base_dir)
            self._404()
            self.server.getreq_busy = False
            return

        if not self._secure_mode():
            if self.server.debug:
                print('WARN: Unauthorized GET')
            self._404()
            self.server.getreq_busy = False
            return

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'authorized fetch',
                            self.server.debug)

        # check that the file exists
        filename = self.server.base_dir + self.path
        if os.path.isfile(filename):
            content = None
            try:
                with open(filename, 'r', encoding='utf-8') as rfile:
                    content = rfile.read()
            except OSError:
                print('EX: unable to read file ' + filename)
            if content:
                content_json = json.loads(content)
                msg = json.dumps(content_json,
                                 ensure_ascii=False).encode('utf-8')
                msglen = len(msg)
                self._set_headers('application/json',
                                  msglen,
                                  None, calling_domain, False)
                self._write(msg)
                fitness_performance(getreq_start_time, self.server.fitness,
                                    '_GET', 'arbitrary json',
                                    self.server.debug)
        else:
            if self.server.debug:
                print('DEBUG: GET Unknown file')
            self._404()
        self.server.getreq_busy = False

        fitness_performance(getreq_start_time, self.server.fitness,
                            '_GET', 'end benchmarks',
                            self.server.debug)

    def do_HEAD(self):
        calling_domain = self.server.domain_full
        if self.headers.get('Host'):
            calling_domain = decoded_host(self.headers['Host'])
            if self.server.onion_domain:
                if calling_domain not in (self.server.domain,
                                          self.server.domain_full,
                                          self.server.onion_domain):
                    print('HEAD domain blocked: ' + calling_domain)
                    self._400()
                    return
            else:
                if calling_domain not in (self.server.domain,
                                          self.server.domain_full):
                    print('HEAD domain blocked: ' + calling_domain)
                    self._400()
                    return

        check_path = self.path
        etag = None
        file_length = -1

        if '/media/' in self.path:
            if is_image_file(self.path) or \
               path_is_video(self.path) or \
               path_is_audio(self.path):
                media_str = self.path.split('/media/')[1]
                media_filename = \
                    self.server.base_dir + '/media/' + media_str
                if os.path.isfile(media_filename):
                    check_path = media_filename
                    file_length = os.path.getsize(media_filename)
                    media_tag_filename = media_filename + '.etag'
                    if os.path.isfile(media_tag_filename):
                        try:
                            with open(media_tag_filename, 'r') as efile:
                                etag = efile.read()
                        except OSError:
                            print('EX: do_HEAD unable to read ' +
                                  media_tag_filename)
                    else:
                        media_binary = None
                        try:
                            with open(media_filename, 'rb') as av_file:
                                media_binary = av_file.read()
                        except OSError:
                            print('EX: unable to read media binary ' +
                                  media_filename)
                        if media_binary:
                            etag = md5(media_binary).hexdigest()  # nosec
                            try:
                                with open(media_tag_filename, 'w+') as efile:
                                    efile.write(etag)
                            except OSError:
                                print('EX: do_HEAD unable to write ' +
                                      media_tag_filename)

        media_file_type = media_file_mime_type(check_path)
        self._set_headers_head(media_file_type, file_length,
                               etag, calling_domain, False)

    def _receive_new_post_process(self, post_type: str, path: str, headers: {},
                                  length: int, post_bytes, boundary: str,
                                  calling_domain: str, cookie: str,
                                  authorized: bool,
                                  content_license_url: str) -> int:
        # Note: this needs to happen synchronously
        # 0=this is not a new post
        # 1=new post success
        # -1=new post failed
        # 2=new post canceled
        if self.server.debug:
            print('DEBUG: receiving POST')

        if ' boundary=' in headers['Content-Type']:
            if self.server.debug:
                print('DEBUG: receiving POST headers ' +
                      headers['Content-Type'] +
                      ' path ' + path)
            nickname = None
            nickname_str = path.split('/users/')[1]
            if '?' in nickname_str:
                nickname_str = nickname_str.split('?')[0]
            if '/' in nickname_str:
                nickname = nickname_str.split('/')[0]
            else:
                nickname = nickname_str
            if self.server.debug:
                print('DEBUG: POST nickname ' + str(nickname))
            if not nickname:
                print('WARN: no nickname found when receiving ' + post_type +
                      ' path ' + path)
                return -1
            length = int(headers['Content-Length'])
            if length > self.server.max_post_length:
                print('POST size too large')
                return -1

            boundary = headers['Content-Type'].split('boundary=')[1]
            if ';' in boundary:
                boundary = boundary.split(';')[0]

            # Note: we don't use cgi here because it's due to be deprecated
            # in Python 3.8/3.10
            # Instead we use the multipart mime parser from the email module
            if self.server.debug:
                print('DEBUG: extracting media from POST')
            media_bytes, post_bytes = \
                extract_media_in_form_post(post_bytes, boundary, 'attachpic')
            if self.server.debug:
                if media_bytes:
                    print('DEBUG: media was found. ' +
                          str(len(media_bytes)) + ' bytes')
                else:
                    print('DEBUG: no media was found in POST')

            # Note: a .temp extension is used here so that at no time is
            # an image with metadata publicly exposed, even for a few mS
            filename_base = \
                acct_dir(self.server.base_dir,
                         nickname, self.server.domain) + '/upload.temp'

            filename, attachment_media_type = \
                save_media_in_form_post(media_bytes, self.server.debug,
                                        filename_base)
            if self.server.debug:
                if filename:
                    print('DEBUG: POST media filename is ' + filename)
                else:
                    print('DEBUG: no media filename in POST')

            if filename:
                if is_image_file(filename):
                    post_image_filename = filename.replace('.temp', '')
                    print('Removing metadata from ' + post_image_filename)
                    city = get_spoofed_city(self.server.city,
                                            self.server.base_dir,
                                            nickname, self.server.domain)
                    if self.server.low_bandwidth:
                        convert_image_to_low_bandwidth(filename)
                    process_meta_data(self.server.base_dir,
                                      nickname, self.server.domain,
                                      filename, post_image_filename, city,
                                      content_license_url)
                    if os.path.isfile(post_image_filename):
                        print('POST media saved to ' + post_image_filename)
                    else:
                        print('ERROR: POST media could not be saved to ' +
                              post_image_filename)
                else:
                    if os.path.isfile(filename):
                        new_filename = filename.replace('.temp', '')
                        os.rename(filename, new_filename)
                        filename = new_filename

            fields = \
                extract_text_fields_in_post(post_bytes, boundary,
                                            self.server.debug)
            if self.server.debug:
                if fields:
                    print('DEBUG: text field extracted from POST ' +
                          str(fields))
                else:
                    print('WARN: no text fields could be extracted from POST')

            # was the citations button pressed on the newblog screen?
            citations_button_press = False
            if post_type == 'newblog' and fields.get('submitCitations'):
                if fields['submitCitations'] == \
                   self.server.translate['Citations']:
                    citations_button_press = True

            if not citations_button_press:
                # process the received text fields from the POST
                if not fields.get('message') and \
                   not fields.get('imageDescription') and \
                   not fields.get('pinToProfile'):
                    print('WARN: no message, image description or pin')
                    return -1
                submit_text = self.server.translate['Submit']
                custom_submit_text = \
                    get_config_param(self.server.base_dir, 'customSubmitText')
                if custom_submit_text:
                    submit_text = custom_submit_text
                if fields.get('submitPost'):
                    if fields['submitPost'] != submit_text:
                        print('WARN: no submit field ' + fields['submitPost'])
                        return -1
                else:
                    print('WARN: no submitPost')
                    return 2

            if not fields.get('imageDescription'):
                fields['imageDescription'] = None
            if not fields.get('subject'):
                fields['subject'] = None
            if not fields.get('replyTo'):
                fields['replyTo'] = None

            if not fields.get('schedulePost'):
                fields['schedulePost'] = False
            else:
                fields['schedulePost'] = True
            print('DEBUG: shedulePost ' + str(fields['schedulePost']))

            if not fields.get('eventDate'):
                fields['eventDate'] = None
            if not fields.get('eventTime'):
                fields['eventTime'] = None
            if not fields.get('location'):
                fields['location'] = None

            if not citations_button_press:
                # Store a file which contains the time in seconds
                # since epoch when an attempt to post something was made.
                # This is then used for active monthly users counts
                last_used_filename = \
                    acct_dir(self.server.base_dir,
                             nickname, self.server.domain) + '/.lastUsed'
                try:
                    with open(last_used_filename, 'w+') as lastfile:
                        lastfile.write(str(int(time.time())))
                except OSError:
                    print('EX: _receive_new_post_process unable to write ' +
                          last_used_filename)

            mentions_str = ''
            if fields.get('mentions'):
                mentions_str = fields['mentions'].strip() + ' '
            if not fields.get('commentsEnabled'):
                comments_enabled = False
            else:
                comments_enabled = True

            if post_type == 'newpost':
                if not fields.get('pinToProfile'):
                    pin_to_profile = False
                else:
                    pin_to_profile = True
                    # is the post message empty?
                    if not fields['message']:
                        # remove the pinned content from profile screen
                        undo_pinned_post(self.server.base_dir,
                                         nickname, self.server.domain)
                        return 1

                city = get_spoofed_city(self.server.city,
                                        self.server.base_dir,
                                        nickname, self.server.domain)
                conversation_id = None
                if fields.get('conversationId'):
                    conversation_id = fields['conversationId']

                languages_understood = \
                    get_understood_languages(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain_full,
                                             self.server.person_cache)

                message_json = \
                    create_public_post(self.server.base_dir,
                                       nickname,
                                       self.server.domain,
                                       self.server.port,
                                       self.server.http_prefix,
                                       mentions_str + fields['message'],
                                       False, False, False, comments_enabled,
                                       filename, attachment_media_type,
                                       fields['imageDescription'],
                                       city,
                                       fields['replyTo'], fields['replyTo'],
                                       fields['subject'],
                                       fields['schedulePost'],
                                       fields['eventDate'],
                                       fields['eventTime'],
                                       fields['location'], False,
                                       self.server.system_language,
                                       conversation_id,
                                       self.server.low_bandwidth,
                                       self.server.content_license_url,
                                       languages_understood)
                if message_json:
                    if fields['schedulePost']:
                        return 1
                    if pin_to_profile:
                        sys_language = self.server.system_language
                        content_str = \
                            get_base_content_from_post(message_json,
                                                       sys_language)
                        followers_only = False
                        pin_post(self.server.base_dir,
                                 nickname, self.server.domain, content_str,
                                 followers_only)
                        return 1
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        populate_replies(self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain_full,
                                         message_json,
                                         self.server.max_replies,
                                         self.server.debug)
                        return 1
                    else:
                        return -1
            elif post_type == 'newblog':
                # citations button on newblog screen
                if citations_button_press:
                    message_json = \
                        html_citations(self.server.base_dir,
                                       nickname,
                                       self.server.domain,
                                       self.server.http_prefix,
                                       self.server.default_timeline,
                                       self.server.translate,
                                       self.server.newswire,
                                       self.server.css_cache,
                                       fields['subject'],
                                       fields['message'],
                                       filename, attachment_media_type,
                                       fields['imageDescription'],
                                       self.server.theme_name)
                    if message_json:
                        message_json = message_json.encode('utf-8')
                        message_json_len = len(message_json)
                        self._set_headers('text/html',
                                          message_json_len,
                                          cookie, calling_domain, False)
                        self._write(message_json)
                        return 1
                    else:
                        return -1
                if not fields['subject']:
                    print('WARN: blog posts must have a title')
                    return -1
                if not fields['message']:
                    print('WARN: blog posts must have content')
                    return -1
                # submit button on newblog screen
                followers_only = False
                save_to_file = False
                client_to_server = False
                city = None
                conversation_id = None
                if fields.get('conversationId'):
                    conversation_id = fields['conversationId']
                languages_understood = \
                    get_understood_languages(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain_full,
                                             self.server.person_cache)
                message_json = \
                    create_blog_post(self.server.base_dir, nickname,
                                     self.server.domain, self.server.port,
                                     self.server.http_prefix,
                                     fields['message'],
                                     followers_only, save_to_file,
                                     client_to_server, comments_enabled,
                                     filename, attachment_media_type,
                                     fields['imageDescription'],
                                     city,
                                     fields['replyTo'], fields['replyTo'],
                                     fields['subject'],
                                     fields['schedulePost'],
                                     fields['eventDate'],
                                     fields['eventTime'],
                                     fields['location'],
                                     self.server.system_language,
                                     conversation_id,
                                     self.server.low_bandwidth,
                                     self.server.content_license_url,
                                     languages_understood)
                if message_json:
                    if fields['schedulePost']:
                        return 1
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        refresh_newswire(self.server.base_dir)
                        populate_replies(self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain_full,
                                         message_json,
                                         self.server.max_replies,
                                         self.server.debug)
                        return 1
                    else:
                        return -1
            elif post_type == 'editblogpost':
                print('Edited blog post received')
                post_filename = \
                    locate_post(self.server.base_dir,
                                nickname, self.server.domain,
                                fields['postUrl'])
                if os.path.isfile(post_filename):
                    post_json_object = load_json(post_filename)
                    if post_json_object:
                        cached_filename = \
                            acct_dir(self.server.base_dir,
                                     nickname, self.server.domain) + \
                            '/postcache/' + \
                            fields['postUrl'].replace('/', '#') + '.html'
                        if os.path.isfile(cached_filename):
                            print('Edited blog post, removing cached html')
                            try:
                                os.remove(cached_filename)
                            except OSError:
                                print('EX: _receive_new_post_process ' +
                                      'unable to delete ' + cached_filename)
                        # remove from memory cache
                        remove_post_from_cache(post_json_object,
                                               self.server.recent_posts_cache)
                        # change the blog post title
                        post_json_object['object']['summary'] = \
                            fields['subject']
                        # format message
                        tags = []
                        hashtags_dict = {}
                        mentioned_recipients = []
                        fields['message'] = \
                            add_html_tags(self.server.base_dir,
                                          self.server.http_prefix,
                                          nickname, self.server.domain,
                                          fields['message'],
                                          mentioned_recipients,
                                          hashtags_dict, True)
                        # replace emoji with unicode
                        tags = []
                        for _, tag in hashtags_dict.items():
                            tags.append(tag)
                        # get list of tags
                        fields['message'] = \
                            replace_emoji_from_tags(self.server.session,
                                                    self.server.base_dir,
                                                    fields['message'],
                                                    tags, 'content',
                                                    self.server.debug)

                        post_json_object['object']['content'] = \
                            fields['message']
                        content_map = post_json_object['object']['contentMap']
                        content_map[self.server.system_language] = \
                            fields['message']

                        img_description = ''
                        if fields.get('imageDescription'):
                            img_description = fields['imageDescription']

                        if filename:
                            city = get_spoofed_city(self.server.city,
                                                    self.server.base_dir,
                                                    nickname,
                                                    self.server.domain)
                            post_json_object['object'] = \
                                attach_media(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain,
                                             self.server.port,
                                             post_json_object['object'],
                                             filename,
                                             attachment_media_type,
                                             img_description,
                                             city,
                                             self.server.low_bandwidth,
                                             self.server.content_license_url)

                        replace_you_tube(post_json_object,
                                         self.server.yt_replace_domain,
                                         self.server.system_language)
                        replace_twitter(post_json_object,
                                        self.server.twitter_replacement_domain,
                                        self.server.system_language)
                        save_json(post_json_object, post_filename)
                        # also save to the news actor
                        if nickname != 'news':
                            post_filename = \
                                post_filename.replace('#users#' +
                                                      nickname + '#',
                                                      '#users#news#')
                            save_json(post_json_object, post_filename)
                        print('Edited blog post, resaved ' + post_filename)
                        return 1
                    else:
                        print('Edited blog post, unable to load json for ' +
                              post_filename)
                else:
                    print('Edited blog post not found ' +
                          str(fields['postUrl']))
                return -1
            elif post_type == 'newunlisted':
                city = get_spoofed_city(self.server.city,
                                        self.server.base_dir,
                                        nickname,
                                        self.server.domain)
                followers_only = False
                save_to_file = False
                client_to_server = False

                conversation_id = None
                if fields.get('conversationId'):
                    conversation_id = fields['conversationId']

                languages_understood = \
                    get_understood_languages(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain_full,
                                             self.server.person_cache)

                message_json = \
                    create_unlisted_post(self.server.base_dir,
                                         nickname,
                                         self.server.domain, self.server.port,
                                         self.server.http_prefix,
                                         mentions_str + fields['message'],
                                         followers_only, save_to_file,
                                         client_to_server, comments_enabled,
                                         filename, attachment_media_type,
                                         fields['imageDescription'],
                                         city,
                                         fields['replyTo'],
                                         fields['replyTo'],
                                         fields['subject'],
                                         fields['schedulePost'],
                                         fields['eventDate'],
                                         fields['eventTime'],
                                         fields['location'],
                                         self.server.system_language,
                                         conversation_id,
                                         self.server.low_bandwidth,
                                         self.server.content_license_url,
                                         languages_understood)
                if message_json:
                    if fields['schedulePost']:
                        return 1
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        populate_replies(self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         message_json,
                                         self.server.max_replies,
                                         self.server.debug)
                        return 1
                    else:
                        return -1
            elif post_type == 'newfollowers':
                city = get_spoofed_city(self.server.city,
                                        self.server.base_dir,
                                        nickname,
                                        self.server.domain)
                followers_only = True
                save_to_file = False
                client_to_server = False

                conversation_id = None
                if fields.get('conversationId'):
                    conversation_id = fields['conversationId']

                mentions_message = mentions_str + fields['message']
                languages_understood = \
                    get_understood_languages(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain_full,
                                             self.server.person_cache)
                message_json = \
                    create_followers_only_post(self.server.base_dir,
                                               nickname,
                                               self.server.domain,
                                               self.server.port,
                                               self.server.http_prefix,
                                               mentions_message,
                                               followers_only, save_to_file,
                                               client_to_server,
                                               comments_enabled,
                                               filename, attachment_media_type,
                                               fields['imageDescription'],
                                               city,
                                               fields['replyTo'],
                                               fields['replyTo'],
                                               fields['subject'],
                                               fields['schedulePost'],
                                               fields['eventDate'],
                                               fields['eventTime'],
                                               fields['location'],
                                               self.server.system_language,
                                               conversation_id,
                                               self.server.low_bandwidth,
                                               self.server.content_license_url,
                                               languages_understood)
                if message_json:
                    if fields['schedulePost']:
                        return 1
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        populate_replies(self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         message_json,
                                         self.server.max_replies,
                                         self.server.debug)
                        return 1
                    else:
                        return -1
            elif post_type == 'newdm':
                message_json = None
                print('A DM was posted')
                if '@' in mentions_str:
                    city = get_spoofed_city(self.server.city,
                                            self.server.base_dir,
                                            nickname,
                                            self.server.domain)
                    followers_only = True
                    save_to_file = False
                    client_to_server = False

                    conversation_id = None
                    if fields.get('conversationId'):
                        conversation_id = fields['conversationId']
                    content_license_url = self.server.content_license_url

                    languages_understood = \
                        get_understood_languages(self.server.base_dir,
                                                 self.server.http_prefix,
                                                 nickname,
                                                 self.server.domain_full,
                                                 self.server.person_cache)

                    message_json = \
                        create_direct_message_post(self.server.base_dir,
                                                   nickname,
                                                   self.server.domain,
                                                   self.server.port,
                                                   self.server.http_prefix,
                                                   mentions_str +
                                                   fields['message'],
                                                   followers_only,
                                                   save_to_file,
                                                   client_to_server,
                                                   comments_enabled,
                                                   filename,
                                                   attachment_media_type,
                                                   fields['imageDescription'],
                                                   city,
                                                   fields['replyTo'],
                                                   fields['replyTo'],
                                                   fields['subject'],
                                                   True,
                                                   fields['schedulePost'],
                                                   fields['eventDate'],
                                                   fields['eventTime'],
                                                   fields['location'],
                                                   self.server.system_language,
                                                   conversation_id,
                                                   self.server.low_bandwidth,
                                                   content_license_url,
                                                   languages_understood)
                if message_json:
                    if fields['schedulePost']:
                        return 1
                    print('Sending new DM to ' +
                          str(message_json['object']['to']))
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        populate_replies(self.server.base_dir,
                                         self.server.http_prefix,
                                         self.server.domain,
                                         message_json,
                                         self.server.max_replies,
                                         self.server.debug)
                        return 1
                    else:
                        return -1
            elif post_type == 'newreminder':
                message_json = None
                handle = nickname + '@' + self.server.domain_full
                print('A reminder was posted for ' + handle)
                if '@' + handle not in mentions_str:
                    mentions_str = '@' + handle + ' ' + mentions_str
                city = get_spoofed_city(self.server.city,
                                        self.server.base_dir,
                                        nickname,
                                        self.server.domain)
                followers_only = True
                save_to_file = False
                client_to_server = False
                comments_enabled = False
                conversation_id = None
                mentions_message = mentions_str + fields['message']
                languages_understood = \
                    get_understood_languages(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain_full,
                                             self.server.person_cache)
                message_json = \
                    create_direct_message_post(self.server.base_dir,
                                               nickname,
                                               self.server.domain,
                                               self.server.port,
                                               self.server.http_prefix,
                                               mentions_message,
                                               followers_only, save_to_file,
                                               client_to_server,
                                               comments_enabled,
                                               filename, attachment_media_type,
                                               fields['imageDescription'],
                                               city,
                                               None, None,
                                               fields['subject'],
                                               True, fields['schedulePost'],
                                               fields['eventDate'],
                                               fields['eventTime'],
                                               fields['location'],
                                               self.server.system_language,
                                               conversation_id,
                                               self.server.low_bandwidth,
                                               self.server.content_license_url,
                                               languages_understood)
                if message_json:
                    if fields['schedulePost']:
                        return 1
                    print('DEBUG: new reminder to ' +
                          str(message_json['object']['to']))
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        return 1
                    return -1
            elif post_type == 'newreport':
                if attachment_media_type:
                    if attachment_media_type != 'image':
                        return -1
                # So as to be sure that this only goes to moderators
                # and not accounts being reported we disable any
                # included fediverse addresses by replacing '@' with '-at-'
                fields['message'] = fields['message'].replace('@', '-at-')
                city = get_spoofed_city(self.server.city,
                                        self.server.base_dir,
                                        nickname,
                                        self.server.domain)
                languages_understood = \
                    get_understood_languages(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain_full,
                                             self.server.person_cache)
                message_json = \
                    create_report_post(self.server.base_dir,
                                       nickname,
                                       self.server.domain, self.server.port,
                                       self.server.http_prefix,
                                       mentions_str + fields['message'],
                                       True, False, False, True,
                                       filename, attachment_media_type,
                                       fields['imageDescription'],
                                       city,
                                       self.server.debug, fields['subject'],
                                       self.server.system_language,
                                       self.server.low_bandwidth,
                                       self.server.content_license_url,
                                       languages_understood)
                if message_json:
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        return 1
                    return -1
            elif post_type == 'newquestion':
                if not fields.get('duration'):
                    return -1
                if not fields.get('message'):
                    return -1
#                questionStr = fields['message']
                q_options = []
                for question_ctr in range(8):
                    if fields.get('questionOption' + str(question_ctr)):
                        q_options.append(fields['questionOption' +
                                                str(question_ctr)])
                if not q_options:
                    return -1
                city = get_spoofed_city(self.server.city,
                                        self.server.base_dir,
                                        nickname,
                                        self.server.domain)
                int_duration = int(fields['duration'])
                languages_understood = \
                    get_understood_languages(self.server.base_dir,
                                             self.server.http_prefix,
                                             nickname,
                                             self.server.domain_full,
                                             self.server.person_cache)
                message_json = \
                    create_question_post(self.server.base_dir,
                                         nickname,
                                         self.server.domain,
                                         self.server.port,
                                         self.server.http_prefix,
                                         fields['message'], q_options,
                                         False, False, False,
                                         comments_enabled,
                                         filename, attachment_media_type,
                                         fields['imageDescription'],
                                         city,
                                         fields['subject'],
                                         int_duration,
                                         self.server.system_language,
                                         self.server.low_bandwidth,
                                         self.server.content_license_url,
                                         languages_understood)
                if message_json:
                    if self.server.debug:
                        print('DEBUG: new Question')
                    if self._post_to_outbox(message_json,
                                            self.server.project_version,
                                            nickname):
                        return 1
                return -1
            elif post_type == 'newshare' or post_type == 'newwanted':
                if not fields.get('itemQty'):
                    print(post_type + ' no itemQty')
                    return -1
                if not fields.get('itemType'):
                    print(post_type + ' no itemType')
                    return -1
                if 'itemPrice' not in fields:
                    print(post_type + ' no itemPrice')
                    return -1
                if 'itemCurrency' not in fields:
                    print(post_type + ' no itemCurrency')
                    return -1
                if not fields.get('category'):
                    print(post_type + ' no category')
                    return -1
                if not fields.get('duration'):
                    print(post_type + ' no duratio')
                    return -1
                if attachment_media_type:
                    if attachment_media_type != 'image':
                        print('Attached media is not an image')
                        return -1
                duration_str = fields['duration']
                if duration_str:
                    if ' ' not in duration_str:
                        duration_str = duration_str + ' days'
                city = get_spoofed_city(self.server.city,
                                        self.server.base_dir,
                                        nickname,
                                        self.server.domain)
                item_qty = 1
                if fields['itemQty']:
                    if is_float(fields['itemQty']):
                        item_qty = float(fields['itemQty'])
                item_price = "0.00"
                item_currency = "EUR"
                if fields['itemPrice']:
                    item_price, item_currency = \
                        get_price_from_string(fields['itemPrice'])
                if fields['itemCurrency']:
                    item_currency = fields['itemCurrency']
                if post_type == 'newshare':
                    print('Adding shared item')
                    shares_file_type = 'shares'
                else:
                    print('Adding wanted item')
                    shares_file_type = 'wanted'
                add_share(self.server.base_dir,
                          self.server.http_prefix,
                          nickname,
                          self.server.domain, self.server.port,
                          fields['subject'],
                          fields['message'],
                          filename,
                          item_qty, fields['itemType'],
                          fields['category'],
                          fields['location'],
                          duration_str,
                          self.server.debug,
                          city, item_price, item_currency,
                          self.server.system_language,
                          self.server.translate, shares_file_type,
                          self.server.low_bandwidth,
                          self.server.content_license_url)
                if filename:
                    if os.path.isfile(filename):
                        try:
                            os.remove(filename)
                        except OSError:
                            print('EX: _receive_new_post_process ' +
                                  'unable to delete ' + filename)
                self.post_to_nickname = nickname
                return 1
        return -1

    def _receive_new_post(self, post_type: str, path: str,
                          calling_domain: str, cookie: str,
                          authorized: bool,
                          content_license_url: str) -> int:
        """A new post has been created
        This creates a thread to send the new post
        """
        page_number = 1

        if '/users/' not in path:
            print('Not receiving new post for ' + path +
                  ' because /users/ not in path')
            return None

        if '?' + post_type + '?' not in path:
            print('Not receiving new post for ' + path +
                  ' because ?' + post_type + '? not in path')
            return None

        print('New post begins: ' + post_type + ' ' + path)

        if '?page=' in path:
            page_number_str = path.split('?page=')[1]
            if '?' in page_number_str:
                page_number_str = page_number_str.split('?')[0]
            if '#' in page_number_str:
                page_number_str = page_number_str.split('#')[0]
            if page_number_str.isdigit():
                page_number = int(page_number_str)
                path = path.split('?page=')[0]

        # get the username who posted
        new_post_thread_name = None
        if '/users/' in path:
            new_post_thread_name = path.split('/users/')[1]
            if '/' in new_post_thread_name:
                new_post_thread_name = new_post_thread_name.split('/')[0]
        if not new_post_thread_name:
            new_post_thread_name = '*'

        if self.server.new_post_thread.get(new_post_thread_name):
            print('Waiting for previous new post thread to end')
            wait_ctr = 0
            np_thread = self.server.new_post_thread[new_post_thread_name]
            while np_thread.is_alive() and wait_ctr < 8:
                time.sleep(1)
                wait_ctr += 1
            if wait_ctr >= 8:
                print('Killing previous new post thread for ' +
                      new_post_thread_name)
                np_thread.kill()

        # make a copy of self.headers
        headers = {}
        headers_without_cookie = {}
        for dict_entry_name, header_line in self.headers.items():
            headers[dict_entry_name] = header_line
            if dict_entry_name.lower() != 'cookie':
                headers_without_cookie[dict_entry_name] = header_line
        print('New post headers: ' + str(headers_without_cookie))

        length = int(headers['Content-Length'])
        if length > self.server.max_post_length:
            print('POST size too large')
            return None

        if not headers.get('Content-Type'):
            if headers.get('Content-type'):
                headers['Content-Type'] = headers['Content-type']
            elif headers.get('content-type'):
                headers['Content-Type'] = headers['content-type']
        if headers.get('Content-Type'):
            if ' boundary=' in headers['Content-Type']:
                boundary = headers['Content-Type'].split('boundary=')[1]
                if ';' in boundary:
                    boundary = boundary.split(';')[0]

                try:
                    post_bytes = self.rfile.read(length)
                except SocketError as ex:
                    if ex.errno == errno.ECONNRESET:
                        print('WARN: POST post_bytes ' +
                              'connection reset by peer')
                    else:
                        print('WARN: POST post_bytes socket error')
                    return None
                except ValueError as ex:
                    print('EX: POST post_bytes rfile.read failed, ' +
                          str(ex))
                    return None

                # second length check from the bytes received
                # since Content-Length could be untruthful
                length = len(post_bytes)
                if length > self.server.max_post_length:
                    print('POST size too large')
                    return None

                # Note sending new posts needs to be synchronous,
                # otherwise any attachments can get mangled if
                # other events happen during their decoding
                print('Creating new post from: ' + new_post_thread_name)
                self._receive_new_post_process(post_type,
                                               path, headers, length,
                                               post_bytes, boundary,
                                               calling_domain, cookie,
                                               authorized,
                                               content_license_url)
        return page_number

    def _crypto_ap_iread_handle(self):
        """Reads handle
        """
        message_bytes = None
        max_device_id_length = 2048
        length = int(self.headers['Content-length'])
        if length >= max_device_id_length:
            print('WARN: handle post to crypto API is too long ' +
                  str(length) + ' bytes')
            return {}
        try:
            message_bytes = self.rfile.read(length)
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('WARN: handle POST message_bytes ' +
                      'connection reset by peer')
            else:
                print('WARN: handle POST message_bytes socket error')
            return {}
        except ValueError as ex:
            print('EX: handle POST message_bytes rfile.read failed ' +
                  str(ex))
            return {}

        len_message = len(message_bytes)
        if len_message > 2048:
            print('WARN: handle post to crypto API is too long ' +
                  str(len_message) + ' bytes')
            return {}

        handle = message_bytes.decode("utf-8")
        if not handle:
            return None
        if '@' not in handle:
            return None
        if '[' in handle:
            return json.loads(message_bytes)
        if handle.startswith('@'):
            handle = handle[1:]
        if '@' not in handle:
            return None
        return handle.strip()

    def _crypto_ap_iread_json(self) -> {}:
        """Obtains json from POST to the crypto API
        """
        message_bytes = None
        max_crypto_message_length = 10240
        length = int(self.headers['Content-length'])
        if length >= max_crypto_message_length:
            print('WARN: post to crypto API is too long ' +
                  str(length) + ' bytes')
            return {}
        try:
            message_bytes = self.rfile.read(length)
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('WARN: POST message_bytes ' +
                      'connection reset by peer')
            else:
                print('WARN: POST message_bytes socket error')
            return {}
        except ValueError as ex:
            print('EX: POST message_bytes rfile.read failed, ' + str(ex))
            return {}

        len_message = len(message_bytes)
        if len_message > 10240:
            print('WARN: post to crypto API is too long ' +
                  str(len_message) + ' bytes')
            return {}

        return json.loads(message_bytes)

    def _crypto_api_query(self, calling_domain: str) -> bool:
        handle = self._crypto_ap_iread_handle()
        if not handle:
            return False
        if isinstance(handle, str):
            person_dir = self.server.base_dir + '/accounts/' + handle
            if not os.path.isdir(person_dir + '/devices'):
                return False
            devices_list = []
            for _, _, files in os.walk(person_dir + '/devices'):
                for fname in files:
                    device_filename = \
                        os.path.join(person_dir + '/devices', fname)
                    if not os.path.isfile(device_filename):
                        continue
                    content_json = load_json(device_filename)
                    if content_json:
                        devices_list.append(content_json)
                break
            # return the list of devices for this handle
            msg = \
                json.dumps(devices_list,
                           ensure_ascii=False).encode('utf-8')
            msglen = len(msg)
            self._set_headers('application/json',
                              msglen,
                              None, calling_domain, False)
            self._write(msg)
            return True
        return False

    def _crypto_api(self, path: str, authorized: bool) -> None:
        """POST or GET with the crypto API
        """
        if authorized and path.startswith('/api/v1/crypto/keys/upload'):
            # register a device to an authorized account
            if not self.authorized_nickname:
                self._400()
                return
            device_keys = self._crypto_ap_iread_json()
            if not device_keys:
                self._400()
                return
            if isinstance(device_keys, dict):
                if not e2e_evalid_device(device_keys):
                    self._400()
                    return
                fingerprint_key = \
                    device_keys['fingerprint_key']['publicKeyBase64']
                e2e_eadd_device(self.server.base_dir,
                                self.authorized_nickname,
                                self.server.domain,
                                device_keys['deviceId'],
                                device_keys['name'],
                                device_keys['claim'],
                                fingerprint_key,
                                device_keys['identityKey']['publicKeyBase64'],
                                device_keys['fingerprint_key']['type'],
                                device_keys['identityKey']['type'])
                self._200()
                return
            self._400()
        elif path.startswith('/api/v1/crypto/keys/query'):
            # given a handle (nickname@domain) return a list of the devices
            # registered to that handle
            if not self._crypto_api_query():
                self._400()
        elif path.startswith('/api/v1/crypto/keys/claim'):
            # TODO
            self._200()
        elif authorized and path.startswith('/api/v1/crypto/delivery'):
            # TODO
            self._200()
        elif (authorized and
              path.startswith('/api/v1/crypto/encrypted_messages/clear')):
            # TODO
            self._200()
        elif path.startswith('/api/v1/crypto/encrypted_messages'):
            # TODO
            self._200()
        else:
            self._400()

    def do_POST(self):
        postreq_start_time = time.time()

        if not self._establish_session("POST"):
            fitness_performance(postreq_start_time, self.server.fitness,
                                '_POST', 'create_session',
                                self.server.debug)
            self._404()
            return

        if self.server.debug:
            print('DEBUG: POST to ' + self.server.base_dir +
                  ' path: ' + self.path + ' busy: ' +
                  str(self.server.postreq_busy))

        calling_domain = self.server.domain_full
        if self.headers.get('Host'):
            calling_domain = decoded_host(self.headers['Host'])
            if self.server.onion_domain:
                if calling_domain != self.server.domain and \
                   calling_domain != self.server.domain_full and \
                   calling_domain != self.server.onion_domain:
                    print('POST domain blocked: ' + calling_domain)
                    self._400()
                    return
            elif self.server.i2p_domain:
                if calling_domain != self.server.domain and \
                   calling_domain != self.server.domain_full and \
                   calling_domain != self.server.i2p_domain:
                    print('POST domain blocked: ' + calling_domain)
                    self._400()
                    return
            else:
                if calling_domain != self.server.domain and \
                   calling_domain != self.server.domain_full:
                    print('POST domain blocked: ' + calling_domain)
                    self._400()
                    return

        curr_time_postreq = int(time.time() * 1000)
        if self.server.postreq_busy:
            if curr_time_postreq - self.server.last_postreq < 500:
                self.send_response(429)
                self.end_headers()
                return
        self.server.postreq_busy = True
        self.server.last_postreq = curr_time_postreq

        ua_str = self._get_user_agent()

        if self._blocked_user_agent(calling_domain, ua_str):
            self._400()
            self.server.postreq_busy = False
            return

        if not self.headers.get('Content-type'):
            print('Content-type header missing')
            self._400()
            self.server.postreq_busy = False
            return

        # returns after this point should set postreq_busy to False

        # remove any trailing slashes from the path
        if not self.path.endswith('confirm'):
            self.path = self.path.replace('/outbox/', '/outbox')
            self.path = self.path.replace('/tlblogs/', '/tlblogs')
            self.path = self.path.replace('/inbox/', '/inbox')
            self.path = self.path.replace('/shares/', '/shares')
            self.path = self.path.replace('/wanted/', '/wanted')
            self.path = self.path.replace('/sharedInbox/', '/sharedInbox')

        if self.path == '/inbox':
            if not self.server.enable_shared_inbox:
                self._503()
                self.server.postreq_busy = False
                return

        cookie = None
        if self.headers.get('Cookie'):
            cookie = self.headers['Cookie']

        # check authorization
        authorized = self._is_authorized()
        if not authorized and self.server.debug:
            print('POST Not authorized')
            print(str(self.headers))

        if self.path.startswith('/api/v1/crypto/'):
            self._crypto_api(self.path, authorized)
            self.server.postreq_busy = False
            return

        # if this is a POST to the outbox then check authentication
        self.outbox_authenticated = False
        self.post_to_nickname = None

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'start',
                            self.server.debug)

        # login screen
        if self.path.startswith('/login'):
            self._show_login_screen(self.path, calling_domain, cookie,
                                    self.server.base_dir,
                                    self.server.http_prefix,
                                    self.server.domain,
                                    self.server.domain_full,
                                    self.server.port,
                                    self.server.onion_domain,
                                    self.server.i2p_domain,
                                    self.server.debug)
            self.server.postreq_busy = False
            return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', '_login_screen',
                            self.server.debug)

        if authorized and self.path.endswith('/sethashtagcategory'):
            self._set_hashtag_category(calling_domain, cookie,
                                       authorized, self.path,
                                       self.server.base_dir,
                                       self.server.http_prefix,
                                       self.server.domain,
                                       self.server.domain_full,
                                       self.server.onion_domain,
                                       self.server.i2p_domain,
                                       self.server.debug,
                                       self.server.default_timeline,
                                       self.server.allow_local_network_access)
            self.server.postreq_busy = False
            return

        # update of profile/avatar from web interface,
        # after selecting Edit button then Submit
        if authorized and self.path.endswith('/profiledata'):
            self._profile_edit(calling_domain, cookie, authorized, self.path,
                               self.server.base_dir, self.server.http_prefix,
                               self.server.domain,
                               self.server.domain_full,
                               self.server.onion_domain,
                               self.server.i2p_domain, self.server.debug,
                               self.server.allow_local_network_access,
                               self.server.system_language,
                               self.server.content_license_url)
            self.server.postreq_busy = False
            return

        if authorized and self.path.endswith('/linksdata'):
            self._links_update(calling_domain, cookie, authorized, self.path,
                               self.server.base_dir, self.server.http_prefix,
                               self.server.domain,
                               self.server.domain_full,
                               self.server.onion_domain,
                               self.server.i2p_domain, self.server.debug,
                               self.server.default_timeline,
                               self.server.allow_local_network_access)
            self.server.postreq_busy = False
            return

        if authorized and self.path.endswith('/newswiredata'):
            self._newswire_update(calling_domain, cookie,
                                  authorized, self.path,
                                  self.server.base_dir,
                                  self.server.http_prefix,
                                  self.server.domain,
                                  self.server.domain_full,
                                  self.server.onion_domain,
                                  self.server.i2p_domain, self.server.debug,
                                  self.server.default_timeline)
            self.server.postreq_busy = False
            return

        if authorized and self.path.endswith('/citationsdata'):
            self._citations_update(calling_domain, cookie,
                                   authorized, self.path,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain,
                                   self.server.domain_full,
                                   self.server.onion_domain,
                                   self.server.i2p_domain, self.server.debug,
                                   self.server.default_timeline,
                                   self.server.newswire)
            self.server.postreq_busy = False
            return

        if authorized and self.path.endswith('/newseditdata'):
            self._news_post_edit(calling_domain, cookie, authorized, self.path,
                                 self.server.base_dir, self.server.http_prefix,
                                 self.server.domain,
                                 self.server.domain_full,
                                 self.server.onion_domain,
                                 self.server.i2p_domain, self.server.debug,
                                 self.server.default_timeline)
            self.server.postreq_busy = False
            return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', '_news_post_edit',
                            self.server.debug)

        users_in_path = False
        if '/users/' in self.path:
            users_in_path = True

        # moderator action buttons
        if authorized and users_in_path and \
           self.path.endswith('/moderationaction'):
            self._moderator_actions(self.path, calling_domain, cookie,
                                    self.server.base_dir,
                                    self.server.http_prefix,
                                    self.server.domain,
                                    self.server.domain_full,
                                    self.server.port,
                                    self.server.onion_domain,
                                    self.server.i2p_domain,
                                    self.server.debug)
            self.server.postreq_busy = False
            return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', '_moderator_actions',
                            self.server.debug)

        search_for_emoji = False
        if self.path.endswith('/searchhandleemoji'):
            search_for_emoji = True
            self.path = self.path.replace('/searchhandleemoji',
                                          '/searchhandle')
            if self.server.debug:
                print('DEBUG: searching for emoji')
                print('authorized: ' + str(authorized))

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'searchhandleemoji',
                            self.server.debug)

        # a search was made
        if ((authorized or search_for_emoji) and
            (self.path.endswith('/searchhandle') or
             '/searchhandle?page=' in self.path)):
            self._receive_search_query(calling_domain, cookie,
                                       authorized, self.path,
                                       self.server.base_dir,
                                       self.server.http_prefix,
                                       self.server.domain,
                                       self.server.domain_full,
                                       self.server.port,
                                       search_for_emoji,
                                       self.server.onion_domain,
                                       self.server.i2p_domain,
                                       postreq_start_time, {},
                                       self.server.debug)
            self.server.postreq_busy = False
            return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', '_receive_search_query',
                            self.server.debug)

        if not authorized:
            if self.path.endswith('/rmpost'):
                print('ERROR: attempt to remove post was not authorized. ' +
                      self.path)
                self._400()
                self.server.postreq_busy = False
                return
        else:
            # a vote/question/poll is posted
            if self.path.endswith('/question') or \
               '/question?page=' in self.path:
                self._receive_vote(calling_domain, cookie,
                                   authorized, self.path,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain,
                                   self.server.domain_full,
                                   self.server.onion_domain,
                                   self.server.i2p_domain,
                                   self.server.debug)
                self.server.postreq_busy = False
                return

            # removes a shared item
            if self.path.endswith('/rmshare'):
                self._remove_share(calling_domain, cookie,
                                   authorized, self.path,
                                   self.server.base_dir,
                                   self.server.http_prefix,
                                   self.server.domain,
                                   self.server.domain_full,
                                   self.server.onion_domain,
                                   self.server.i2p_domain,
                                   self.server.debug)
                self.server.postreq_busy = False
                return

            # removes a wanted item
            if self.path.endswith('/rmwanted'):
                self._remove_wanted(calling_domain, cookie,
                                    authorized, self.path,
                                    self.server.base_dir,
                                    self.server.http_prefix,
                                    self.server.domain,
                                    self.server.domain_full,
                                    self.server.onion_domain,
                                    self.server.i2p_domain,
                                    self.server.debug)
                self.server.postreq_busy = False
                return

            fitness_performance(postreq_start_time, self.server.fitness,
                                '_POST', '_remove_wanted',
                                self.server.debug)

            # removes a post
            if self.path.endswith('/rmpost'):
                if '/users/' not in self.path:
                    print('ERROR: attempt to remove post ' +
                          'was not authorized. ' + self.path)
                    self._400()
                    self.server.postreq_busy = False
                    return
            if self.path.endswith('/rmpost'):
                self._receive_remove_post(calling_domain, cookie,
                                          authorized, self.path,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          self.server.debug)
                self.server.postreq_busy = False
                return

            fitness_performance(postreq_start_time, self.server.fitness,
                                '_POST', '_remove_post',
                                self.server.debug)

            # decision to follow in the web interface is confirmed
            if self.path.endswith('/followconfirm'):
                self._follow_confirm(calling_domain, cookie,
                                     authorized, self.path,
                                     self.server.base_dir,
                                     self.server.http_prefix,
                                     self.server.domain,
                                     self.server.domain_full,
                                     self.server.port,
                                     self.server.onion_domain,
                                     self.server.i2p_domain,
                                     self.server.debug)
                self.server.postreq_busy = False
                return

            fitness_performance(postreq_start_time, self.server.fitness,
                                '_POST', '_follow_confirm',
                                self.server.debug)

            # decision to unfollow in the web interface is confirmed
            if self.path.endswith('/unfollowconfirm'):
                self._unfollow_confirm(calling_domain, cookie,
                                       authorized, self.path,
                                       self.server.base_dir,
                                       self.server.http_prefix,
                                       self.server.domain,
                                       self.server.domain_full,
                                       self.server.port,
                                       self.server.onion_domain,
                                       self.server.i2p_domain,
                                       self.server.debug)
                self.server.postreq_busy = False
                return

            fitness_performance(postreq_start_time, self.server.fitness,
                                '_POST', '_unfollow_confirm',
                                self.server.debug)

            # decision to unblock in the web interface is confirmed
            if self.path.endswith('/unblockconfirm'):
                self._unblock_confirm(calling_domain, cookie,
                                      authorized, self.path,
                                      self.server.base_dir,
                                      self.server.http_prefix,
                                      self.server.domain,
                                      self.server.domain_full,
                                      self.server.port,
                                      self.server.onion_domain,
                                      self.server.i2p_domain,
                                      self.server.debug)
                self.server.postreq_busy = False
                return

            fitness_performance(postreq_start_time, self.server.fitness,
                                '_POST', '_unblock_confirm',
                                self.server.debug)

            # decision to block in the web interface is confirmed
            if self.path.endswith('/blockconfirm'):
                self._block_confirm(calling_domain, cookie,
                                    authorized, self.path,
                                    self.server.base_dir,
                                    self.server.http_prefix,
                                    self.server.domain,
                                    self.server.domain_full,
                                    self.server.port,
                                    self.server.onion_domain,
                                    self.server.i2p_domain,
                                    self.server.debug)
                self.server.postreq_busy = False
                return

            fitness_performance(postreq_start_time, self.server.fitness,
                                '_POST', '_block_confirm',
                                self.server.debug)

            # an option was chosen from person options screen
            # view/follow/block/report
            if self.path.endswith('/personoptions'):
                self._person_options(self.path,
                                     calling_domain, cookie,
                                     self.server.base_dir,
                                     self.server.http_prefix,
                                     self.server.domain,
                                     self.server.domain_full,
                                     self.server.port,
                                     self.server.onion_domain,
                                     self.server.i2p_domain,
                                     self.server.debug)
                self.server.postreq_busy = False
                return

            # Change the key shortcuts
            if users_in_path and \
               self.path.endswith('/changeAccessKeys'):
                nickname = self.path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]

                if not self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.access_keys
                    self.server.key_shortcuts[nickname] = access_keys.copy()
                access_keys = self.server.key_shortcuts[nickname]

                self._key_shortcuts(self.path,
                                    calling_domain, cookie,
                                    self.server.base_dir,
                                    self.server.http_prefix,
                                    nickname,
                                    self.server.domain,
                                    self.server.domain_full,
                                    self.server.port,
                                    self.server.onion_domain,
                                    self.server.i2p_domain,
                                    self.server.debug,
                                    access_keys,
                                    self.server.default_timeline)
                self.server.postreq_busy = False
                return

            # theme designer submit/cancel button
            if users_in_path and \
               self.path.endswith('/changeThemeSettings'):
                nickname = self.path.split('/users/')[1]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]

                if not self.server.key_shortcuts.get(nickname):
                    access_keys = self.server.access_keys
                    self.server.key_shortcuts[nickname] = access_keys.copy()
                access_keys = self.server.key_shortcuts[nickname]
                allow_local_network_access = \
                    self.server.allow_local_network_access

                self._theme_designer_edit(self.path,
                                          calling_domain, cookie,
                                          self.server.base_dir,
                                          self.server.http_prefix,
                                          nickname,
                                          self.server.domain,
                                          self.server.domain_full,
                                          self.server.port,
                                          self.server.onion_domain,
                                          self.server.i2p_domain,
                                          self.server.debug,
                                          access_keys,
                                          self.server.default_timeline,
                                          self.server.theme_name,
                                          allow_local_network_access,
                                          self.server.system_language,
                                          self.server.dyslexic_font)
                self.server.postreq_busy = False
                return

        # update the shared item federation token for the calling domain
        # if it is within the permitted federation
        if self.headers.get('Origin') and \
           self.headers.get('SharesCatalog'):
            if self.server.debug:
                print('SharesCatalog header: ' + self.headers['SharesCatalog'])
            if not self.server.shared_items_federated_domains:
                si_domains_str = \
                    get_config_param(self.server.base_dir,
                                     'sharedItemsFederatedDomains')
                if si_domains_str:
                    if self.server.debug:
                        print('Loading shared items federated domains list')
                    si_domains_list = si_domains_str.split(',')
                    domains_list = self.server.shared_items_federated_domains
                    for si_domain in si_domains_list:
                        domains_list.append(si_domain.strip())
            origin_domain = self.headers.get('Origin')
            if origin_domain != self.server.domain_full and \
               origin_domain != self.server.onion_domain and \
               origin_domain != self.server.i2p_domain and \
               origin_domain in self.server.shared_items_federated_domains:
                if self.server.debug:
                    print('DEBUG: ' +
                          'POST updating shared item federation ' +
                          'token for ' + origin_domain + ' to ' +
                          self.server.domain_full)
                shared_item_tokens = self.server.shared_item_federation_tokens
                shares_token = self.headers['SharesCatalog']
                self.server.shared_item_federation_tokens = \
                    update_shared_item_federation_token(self.server.base_dir,
                                                        origin_domain,
                                                        shares_token,
                                                        self.server.debug,
                                                        shared_item_tokens)
            elif self.server.debug:
                fed_domains = self.server.shared_items_federated_domains
                if origin_domain not in fed_domains:
                    print('origin_domain is not in federated domains list ' +
                          origin_domain)
                else:
                    print('origin_domain is not a different instance. ' +
                          origin_domain + ' ' + self.server.domain_full + ' ' +
                          str(fed_domains))

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'SharesCatalog',
                            self.server.debug)

        # receive different types of post created by html_new_post
        new_post_endpoints = get_new_post_endpoints()
        for curr_post_type in new_post_endpoints:
            if not authorized:
                if self.server.debug:
                    print('POST was not authorized')
                break

            post_redirect = self.server.default_timeline
            if curr_post_type == 'newshare':
                post_redirect = 'tlshares'
            elif curr_post_type == 'newwanted':
                post_redirect = 'tlwanted'

            page_number = \
                self._receive_new_post(curr_post_type, self.path,
                                       calling_domain, cookie,
                                       authorized,
                                       self.server.content_license_url)
            if page_number:
                print(curr_post_type + ' post received')
                nickname = self.path.split('/users/')[1]
                if '?' in nickname:
                    nickname = nickname.split('?')[0]
                if '/' in nickname:
                    nickname = nickname.split('/')[0]

                if calling_domain.endswith('.onion') and \
                   self.server.onion_domain:
                    actor_path_str = \
                        local_actor_url('http', nickname,
                                        self.server.onion_domain) + \
                        '/' + post_redirect + \
                        '?page=' + str(page_number)
                    self._redirect_headers(actor_path_str, cookie,
                                           calling_domain)
                elif (calling_domain.endswith('.i2p') and
                      self.server.i2p_domain):
                    actor_path_str = \
                        local_actor_url('http', nickname,
                                        self.server.i2p_domain) + \
                        '/' + post_redirect + \
                        '?page=' + str(page_number)
                    self._redirect_headers(actor_path_str, cookie,
                                           calling_domain)
                else:
                    actor_path_str = \
                        local_actor_url(self.server.http_prefix, nickname,
                                        self.server.domain_full) + \
                        '/' + post_redirect + '?page=' + str(page_number)
                    self._redirect_headers(actor_path_str, cookie,
                                           calling_domain)
                self.server.postreq_busy = False
                return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'receive post',
                            self.server.debug)

        if self.path.endswith('/outbox') or \
           self.path.endswith('/wanted') or \
           self.path.endswith('/shares'):
            if users_in_path:
                if authorized:
                    self.outbox_authenticated = True
                    path_users_section = self.path.split('/users/')[1]
                    self.post_to_nickname = path_users_section.split('/')[0]
            if not self.outbox_authenticated:
                self.send_response(405)
                self.end_headers()
                self.server.postreq_busy = False
                return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'authorized',
                            self.server.debug)

        # check that the post is to an expected path
        if not (self.path.endswith('/outbox') or
                self.path.endswith('/inbox') or
                self.path.endswith('/wanted') or
                self.path.endswith('/shares') or
                self.path.endswith('/moderationaction') or
                self.path == '/sharedInbox'):
            print('Attempt to POST to invalid path ' + self.path)
            self._400()
            self.server.postreq_busy = False
            return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'check path',
                            self.server.debug)

        # read the message and convert it into a python dictionary
        length = int(self.headers['Content-length'])
        if self.server.debug:
            print('DEBUG: content-length: ' + str(length))
        if not self.headers['Content-type'].startswith('image/') and \
           not self.headers['Content-type'].startswith('video/') and \
           not self.headers['Content-type'].startswith('audio/'):
            if length > self.server.maxMessageLength:
                print('Maximum message length exceeded ' + str(length))
                self._400()
                self.server.postreq_busy = False
                return
        else:
            if length > self.server.maxMediaSize:
                print('Maximum media size exceeded ' + str(length))
                self._400()
                self.server.postreq_busy = False
                return

        # receive images to the outbox
        if self.headers['Content-type'].startswith('image/') and \
           users_in_path:
            self._receive_image(length, calling_domain, cookie,
                                authorized, self.path,
                                self.server.base_dir,
                                self.server.http_prefix,
                                self.server.domain,
                                self.server.domain_full,
                                self.server.onion_domain,
                                self.server.i2p_domain,
                                self.server.debug)
            self.server.postreq_busy = False
            return

        # refuse to receive non-json content
        content_type_str = self.headers['Content-type']
        if not content_type_str.startswith('application/json') and \
           not content_type_str.startswith('application/activity+json') and \
           not content_type_str.startswith('application/ld+json'):
            print("POST is not json: " + self.headers['Content-type'])
            if self.server.debug:
                print(str(self.headers))
                length = int(self.headers['Content-length'])
                if length < self.server.max_post_length:
                    try:
                        unknown_post = self.rfile.read(length).decode('utf-8')
                    except SocketError as ex:
                        if ex.errno == errno.ECONNRESET:
                            print('EX: POST unknown_post ' +
                                  'connection reset by peer')
                        else:
                            print('EX: POST unknown_post socket error')
                        self.send_response(400)
                        self.end_headers()
                        self.server.postreq_busy = False
                        return
                    except ValueError as ex:
                        print('EX: POST unknown_post rfile.read failed, ' +
                              str(ex))
                        self.send_response(400)
                        self.end_headers()
                        self.server.postreq_busy = False
                        return
                    print(str(unknown_post))
            self._400()
            self.server.postreq_busy = False
            return

        if self.server.debug:
            print('DEBUG: Reading message')

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'check content type',
                            self.server.debug)

        # check content length before reading bytes
        if self.path == '/sharedInbox' or self.path == '/inbox':
            length = 0
            if self.headers.get('Content-length'):
                length = int(self.headers['Content-length'])
            elif self.headers.get('Content-Length'):
                length = int(self.headers['Content-Length'])
            elif self.headers.get('content-length'):
                length = int(self.headers['content-length'])
            if length > 10240:
                print('WARN: post to shared inbox is too long ' +
                      str(length) + ' bytes')
                self._400()
                self.server.postreq_busy = False
                return

        try:
            message_bytes = self.rfile.read(length)
        except SocketError as ex:
            if ex.errno == errno.ECONNRESET:
                print('WARN: POST message_bytes ' +
                      'connection reset by peer')
            else:
                print('WARN: POST message_bytes socket error')
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return
        except ValueError as ex:
            print('EX: POST message_bytes rfile.read failed, ' + str(ex))
            self.send_response(400)
            self.end_headers()
            self.server.postreq_busy = False
            return

        # check content length after reading bytes
        if self.path == '/sharedInbox' or self.path == '/inbox':
            len_message = len(message_bytes)
            if len_message > 10240:
                print('WARN: post to shared inbox is too long ' +
                      str(len_message) + ' bytes')
                self._400()
                self.server.postreq_busy = False
                return

        if contains_invalid_chars(message_bytes.decode("utf-8")):
            self._400()
            self.server.postreq_busy = False
            return

        # convert the raw bytes to json
        message_json = json.loads(message_bytes)

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'load json',
                            self.server.debug)

        # https://www.w3.org/TR/activitypub/#object-without-create
        if self.outbox_authenticated:
            if self._post_to_outbox(message_json,
                                    self.server.project_version, None):
                if message_json.get('id'):
                    locn_str = remove_id_ending(message_json['id'])
                    self.headers['Location'] = locn_str
                self.send_response(201)
                self.end_headers()
                self.server.postreq_busy = False
                return
            else:
                if self.server.debug:
                    print('Failed to post to outbox')
                self.send_response(403)
                self.end_headers()
                self.server.postreq_busy = False
                return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', '_post_to_outbox',
                            self.server.debug)

        # check the necessary properties are available
        if self.server.debug:
            print('DEBUG: Check message has params')

        if not message_json:
            self.send_response(403)
            self.end_headers()
            self.server.postreq_busy = False
            return

        if self.path.endswith('/inbox') or \
           self.path == '/sharedInbox':
            if not inbox_message_has_params(message_json):
                if self.server.debug:
                    print("DEBUG: inbox message doesn't have the " +
                          "required parameters")
                self.send_response(403)
                self.end_headers()
                self.server.postreq_busy = False
                return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'inbox_message_has_params',
                            self.server.debug)

        header_signature = self._getheader_signature_input()

        if header_signature:
            if 'keyId=' not in header_signature:
                if self.server.debug:
                    print('DEBUG: POST to inbox has no keyId in ' +
                          'header signature parameter')
                self.send_response(403)
                self.end_headers()
                self.server.postreq_busy = False
                return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'keyId check',
                            self.server.debug)

        if not self.server.unit_test:
            if not inbox_permitted_message(self.server.domain,
                                           message_json,
                                           self.server.federation_list):
                if self.server.debug:
                    # https://www.youtube.com/watch?v=K3PrSj9XEu4
                    print('DEBUG: Ah Ah Ah')
                self.send_response(403)
                self.end_headers()
                self.server.postreq_busy = False
                return

        fitness_performance(postreq_start_time, self.server.fitness,
                            '_POST', 'inbox_permitted_message',
                            self.server.debug)

        if self.server.debug:
            print('DEBUG: POST saving to inbox queue')
        if users_in_path:
            path_users_section = self.path.split('/users/')[1]
            if '/' not in path_users_section:
                if self.server.debug:
                    print('DEBUG: This is not a users endpoint')
            else:
                self.post_to_nickname = path_users_section.split('/')[0]
                if self.post_to_nickname:
                    queue_status = \
                        self._update_inbox_queue(self.post_to_nickname,
                                                 message_json, message_bytes)
                    if queue_status >= 0 and queue_status <= 3:
                        self.server.postreq_busy = False
                        return
                    if self.server.debug:
                        print('_update_inbox_queue exited ' +
                              'without doing anything')
                else:
                    if self.server.debug:
                        print('self.post_to_nickname is None')
            self.send_response(403)
            self.end_headers()
            self.server.postreq_busy = False
            return
        else:
            if self.path == '/sharedInbox' or self.path == '/inbox':
                if self.server.debug:
                    print('DEBUG: POST to shared inbox')
                queue_status = \
                    self._update_inbox_queue('inbox', message_json,
                                             message_bytes)
                if queue_status >= 0 and queue_status <= 3:
                    self.server.postreq_busy = False
                    return
        self._200()
        self.server.postreq_busy = False


class PubServerUnitTest(PubServer):
    protocol_version = 'HTTP/1.0'


class EpicyonServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        # surpress connection reset errors
        cls, e = sys.exc_info()[:2]
        if cls is ConnectionResetError:
            if e.errno != errno.ECONNRESET:
                print('ERROR: (EpicyonServer) ' + str(cls) + ", " + str(e))
            pass
        elif cls is BrokenPipeError:
            pass
        else:
            print('ERROR: (EpicyonServer) ' + str(cls) + ", " + str(e))
            return HTTPServer.handle_error(self, request, client_address)


def run_posts_queue(base_dir: str, send_threads: [], debug: bool,
                    timeoutMins: int) -> None:
    """Manages the threads used to send posts
    """
    while True:
        time.sleep(1)
        remove_dormant_threads(base_dir, send_threads, debug, timeoutMins)


def run_shares_expire(version_number: str, base_dir: str) -> None:
    """Expires shares as needed
    """
    while True:
        time.sleep(120)
        expire_shares(base_dir)


def run_posts_watchdog(project_version: str, httpd) -> None:
    """This tries to keep the posts thread running even if it dies
    """
    print('Starting posts queue watchdog')
    posts_queue_original = httpd.thrPostsQueue.clone(run_posts_queue)
    httpd.thrPostsQueue.start()
    while True:
        time.sleep(20)
        if httpd.thrPostsQueue.is_alive():
            continue
        httpd.thrPostsQueue.kill()
        httpd.thrPostsQueue = posts_queue_original.clone(run_posts_queue)
        httpd.thrPostsQueue.start()
        print('Restarting posts queue...')


def run_shares_expire_watchdog(project_version: str, httpd) -> None:
    """This tries to keep the shares expiry thread running even if it dies
    """
    print('Starting shares expiry watchdog')
    shares_expire_original = httpd.thrSharesExpire.clone(run_shares_expire)
    httpd.thrSharesExpire.start()
    while True:
        time.sleep(20)
        if httpd.thrSharesExpire.is_alive():
            continue
        httpd.thrSharesExpire.kill()
        httpd.thrSharesExpire = shares_expire_original.clone(run_shares_expire)
        httpd.thrSharesExpire.start()
        print('Restarting shares expiry...')


def load_tokens(base_dir: str, tokens_dict: {}, tokens_lookup: {}) -> None:
    """Loads shared items access tokens for each account
    """
    for _, dirs, _ in os.walk(base_dir + '/accounts'):
        for handle in dirs:
            if '@' in handle:
                token_filename = base_dir + '/accounts/' + handle + '/.token'
                if not os.path.isfile(token_filename):
                    continue
                nickname = handle.split('@')[0]
                token = None
                try:
                    with open(token_filename, 'r') as fp_tok:
                        token = fp_tok.read()
                except BaseException as ex:
                    print('WARN: Unable to read token for ' +
                          nickname + ' ' + str(ex))
                if not token:
                    continue
                tokens_dict[nickname] = token
                tokens_lookup[token] = nickname
        break


def run_daemon(dyslexic_font: bool,
               content_license_url: str,
               lists_enabled: str,
               default_reply_interval_hrs: int,
               low_bandwidth: bool,
               max_like_count: int,
               shared_items_federated_domains: [],
               user_agents_blocked: [],
               log_login_failures: bool,
               city: str,
               show_node_info_accounts: bool,
               show_node_info_version: bool,
               broch_mode: bool,
               verify_all_signatures: bool,
               send_threads_timeout_mins: int,
               dormant_months: int,
               max_newswire_posts: int,
               allow_local_network_access: bool,
               max_feed_item_size_kb: int,
               publish_button_at_top: bool,
               rss_icon_at_top: bool,
               icons_as_buttons: bool,
               full_width_tl_button_header: bool,
               show_publish_as_icon: bool,
               max_followers: int,
               max_news_posts: int,
               max_mirrored_articles: int,
               max_newswire_feed_size_kb: int,
               max_newswire_postsPerSource: int,
               show_published_date_only: bool,
               voting_time_mins: int,
               positive_voting: bool,
               newswire_votes_threshold: int,
               news_instance: bool,
               blogs_instance: bool,
               media_instance: bool,
               max_recent_posts: int,
               enable_shared_inbox: bool, registration: bool,
               language: str, project_version: str,
               instance_id: str, client_to_server: bool,
               base_dir: str, domain: str,
               onion_domain: str, i2p_domain: str,
               yt_replace_domain: str,
               twitter_replacement_domain: str,
               port: int = 80, proxy_port: int = 80,
               http_prefix: str = 'https',
               fed_list: [] = [],
               max_mentions: int = 10, max_emoji: int = 10,
               secure_mode: bool = False,
               proxy_type: str = None, max_replies: int = 64,
               domain_max_posts_per_day: int = 8640,
               account_max_posts_per_day: int = 864,
               allow_deletion: bool = False,
               debug: bool = False, unit_test: bool = False,
               instance_only_skills_search: bool = False,
               send_threads: [] = [],
               manual_follower_approval: bool = True) -> None:
    if len(domain) == 0:
        domain = 'localhost'
    if '.' not in domain:
        if domain != 'localhost':
            print('Invalid domain: ' + domain)
            return

    if unit_test:
        server_address = (domain, proxy_port)
        pub_handler = partial(PubServerUnitTest)
    else:
        server_address = ('', proxy_port)
        pub_handler = partial(PubServer)

    if not os.path.isdir(base_dir + '/accounts'):
        print('Creating accounts directory')
        os.mkdir(base_dir + '/accounts')

    try:
        httpd = EpicyonServer(server_address, pub_handler)
    except SocketError as ex:
        if ex.errno == errno.ECONNREFUSED:
            print('EX: HTTP server address is already in use. ' +
                  str(server_address))
            return False

        print('EX: HTTP server failed to start. ' + str(ex))
        print('server_address: ' + str(server_address))
        return False

    # scan the theme directory for any svg files containing scripts
    assert not scan_themes_for_scripts(base_dir)

    httpd.post_to_nickname = None

    httpd.nodeinfo_is_active = False

    httpd.dyslexic_font = dyslexic_font

    # license for content of the instance
    if not content_license_url:
        content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    httpd.content_license_url = content_license_url

    # fitness metrics
    fitness_filename = base_dir + '/accounts/fitness.json'
    httpd.fitness = {}
    if os.path.isfile(fitness_filename):
        httpd.fitness = load_json(fitness_filename)

    # initialize authorized fetch key
    httpd.signing_priv_key_pem = None

    httpd.show_node_info_accounts = show_node_info_accounts
    httpd.show_node_info_version = show_node_info_version

    # ASCII/ANSI text banner used in shell browsers, such as Lynx
    httpd.text_mode_banner = get_text_mode_banner(base_dir)

    # key shortcuts SHIFT + ALT + [key]
    httpd.access_keys = {
        'Page up': ',',
        'Page down': '.',
        'submitButton': 'y',
        'followButton': 'f',
        'blockButton': 'b',
        'infoButton': 'i',
        'snoozeButton': 's',
        'reportButton': '[',
        'viewButton': 'v',
        'enterPetname': 'p',
        'enterNotes': 'n',
        'menuTimeline': 't',
        'menuEdit': 'e',
        'menuThemeDesigner': 'z',
        'menuProfile': 'p',
        'menuInbox': 'i',
        'menuSearch': '/',
        'menuNewPost': 'n',
        'menuCalendar': 'c',
        'menuDM': 'd',
        'menuReplies': 'r',
        'menuOutbox': 's',
        'menuBookmarks': 'q',
        'menuShares': 'h',
        'menuWanted': 'w',
        'menuBlogs': 'b',
        'menuNewswire': 'u',
        'menuLinks': 'l',
        'menuMedia': 'm',
        'menuModeration': 'o',
        'menuFollowing': 'f',
        'menuFollowers': 'g',
        'menuRoles': 'o',
        'menuSkills': 'a',
        'menuLogout': 'x',
        'menuKeys': 'k',
        'Public': 'p',
        'Reminder': 'r'
    }

    # how many hours after a post was publushed can a reply be made
    default_reply_interval_hrs = 9999999
    httpd.default_reply_interval_hrs = default_reply_interval_hrs

    httpd.key_shortcuts = {}
    load_access_keys_for_accounts(base_dir, httpd.key_shortcuts,
                                  httpd.access_keys)

    # wheither to use low bandwidth images
    httpd.low_bandwidth = low_bandwidth

    # list of blocked user agent types within the User-Agent header
    httpd.user_agents_blocked = user_agents_blocked

    httpd.unit_test = unit_test
    httpd.allow_local_network_access = allow_local_network_access
    if unit_test:
        # unit tests are run on the local network with LAN addresses
        httpd.allow_local_network_access = True
    httpd.yt_replace_domain = yt_replace_domain
    httpd.twitter_replacement_domain = twitter_replacement_domain

    # newswire storing rss feeds
    httpd.newswire = {}

    # maximum number of posts to appear in the newswire on the right column
    httpd.max_newswire_posts = max_newswire_posts

    # whether to require that all incoming posts have valid jsonld signatures
    httpd.verify_all_signatures = verify_all_signatures

    # This counter is used to update the list of blocked domains in memory.
    # It helps to avoid touching the disk and so improves flooding resistance
    httpd.blocklistUpdateCtr = 0
    httpd.blocklistUpdateInterval = 100
    httpd.domainBlocklist = get_domain_blocklist(base_dir)

    httpd.manual_follower_approval = manual_follower_approval
    if domain.endswith('.onion'):
        onion_domain = domain
    elif domain.endswith('.i2p'):
        i2p_domain = domain
    httpd.onion_domain = onion_domain
    httpd.i2p_domain = i2p_domain
    httpd.media_instance = media_instance
    httpd.blogs_instance = blogs_instance

    # load translations dictionary
    httpd.translate = {}
    httpd.system_language = 'en'
    if not unit_test:
        httpd.translate, httpd.system_language = \
            load_translations_from_file(base_dir, language)
        if not httpd.system_language:
            print('ERROR: no system language loaded')
            sys.exit()
        print('System language: ' + httpd.system_language)
        if not httpd.translate:
            print('ERROR: no translations were loaded')
            sys.exit()

    # spoofed city for gps location misdirection
    httpd.city = city

    # For moderated newswire feeds this is the amount of time allowed
    # for voting after the post arrives
    httpd.voting_time_mins = voting_time_mins
    # on the newswire, whether moderators vote positively for items
    # or against them (veto)
    httpd.positive_voting = positive_voting
    # number of votes needed to remove a newswire item from the news timeline
    # or if positive voting is anabled to add the item to the news timeline
    httpd.newswire_votes_threshold = newswire_votes_threshold
    # maximum overall size of an rss/atom feed read by the newswire daemon
    # If the feed is too large then this is probably a DoS attempt
    httpd.max_newswire_feed_size_kb = max_newswire_feed_size_kb

    # For each newswire source (account or rss feed)
    # this is the maximum number of posts to show for each.
    # This avoids one or two sources from dominating the news,
    # and also prevents big feeds from slowing down page load times
    httpd.max_newswire_postsPerSource = max_newswire_postsPerSource

    # Show only the date at the bottom of posts, and not the time
    httpd.show_published_date_only = show_published_date_only

    # maximum number of news articles to mirror
    httpd.max_mirrored_articles = max_mirrored_articles

    # maximum number of posts in the news timeline/outbox
    httpd.max_news_posts = max_news_posts

    # The maximum number of tags per post which can be
    # attached to RSS feeds pulled in via the newswire
    httpd.maxTags = 32

    # maximum number of followers per account
    httpd.max_followers = max_followers

    # whether to show an icon for publish on the
    # newswire, or a 'Publish' button
    httpd.show_publish_as_icon = show_publish_as_icon

    # Whether to show the timeline header containing inbox, outbox
    # calendar, etc as the full width of the screen or not
    httpd.full_width_tl_button_header = full_width_tl_button_header

    # whether to show icons in the header (eg calendar) as buttons
    httpd.icons_as_buttons = icons_as_buttons

    # whether to show the RSS icon at the top or the bottom of the timeline
    httpd.rss_icon_at_top = rss_icon_at_top

    # Whether to show the newswire publish button at the top,
    # above the header image
    httpd.publish_button_at_top = publish_button_at_top

    # maximum size of individual RSS feed items, in K
    httpd.max_feed_item_size_kb = max_feed_item_size_kb

    # maximum size of a hashtag category, in K
    httpd.maxCategoriesFeedItemSizeKb = 1024

    # how many months does a followed account need to be unseen
    # for it to be considered dormant?
    httpd.dormant_months = dormant_months

    # maximum number of likes to display on a post
    httpd.max_like_count = max_like_count
    if httpd.max_like_count < 0:
        httpd.max_like_count = 0
    elif httpd.max_like_count > 16:
        httpd.max_like_count = 16

    httpd.followingItemsPerPage = 12
    if registration == 'open':
        httpd.registration = True
    else:
        httpd.registration = False
    httpd.enable_shared_inbox = enable_shared_inbox
    httpd.outboxThread = {}
    httpd.outbox_thread_index = {}
    httpd.new_post_thread = {}
    httpd.project_version = project_version
    httpd.secure_mode = secure_mode
    # max POST size of 30M
    httpd.max_post_length = 1024 * 1024 * 30
    httpd.maxMediaSize = httpd.max_post_length
    # Maximum text length is 64K - enough for a blog post
    httpd.maxMessageLength = 64000
    # Maximum overall number of posts per box
    httpd.maxPostsInBox = 32000
    httpd.domain = domain
    httpd.port = port
    httpd.domain_full = get_full_domain(domain, port)
    save_domain_qrcode(base_dir, http_prefix, httpd.domain_full)
    httpd.http_prefix = http_prefix
    httpd.debug = debug
    httpd.federation_list = fed_list.copy()
    httpd.shared_items_federated_domains = \
        shared_items_federated_domains.copy()
    httpd.base_dir = base_dir
    httpd.instance_id = instance_id
    httpd.person_cache = {}
    httpd.cached_webfingers = {}
    httpd.favicons_cache = {}
    httpd.proxy_type = proxy_type
    httpd.session = None
    httpd.session_last_update = 0
    httpd.last_getreq = 0
    httpd.last_postreq = 0
    httpd.getreq_busy = False
    httpd.postreq_busy = False
    httpd.received_message = False
    httpd.inbox_queue = []
    httpd.send_threads = send_threads
    httpd.postLog = []
    httpd.max_queue_length = 64
    httpd.allow_deletion = allow_deletion
    httpd.last_login_time = 0
    httpd.last_login_failure = 0
    httpd.login_failure_count = {}
    httpd.log_login_failures = log_login_failures
    httpd.max_replies = max_replies
    httpd.tokens = {}
    httpd.tokens_lookup = {}
    load_tokens(base_dir, httpd.tokens, httpd.tokens_lookup)
    httpd.instance_only_skills_search = instance_only_skills_search
    # contains threads used to send posts to followers
    httpd.followers_threads = []

    # create a cache of blocked domains in memory.
    # This limits the amount of slow disk reads which need to be done
    httpd.blocked_cache = []
    httpd.blocked_cache_last_updated = 0
    httpd.blocked_cache_update_secs = 120
    httpd.blocked_cache_last_updated = \
        update_blocked_cache(base_dir, httpd.blocked_cache,
                             httpd.blocked_cache_last_updated,
                             httpd.blocked_cache_update_secs)

    # cache to store css files
    httpd.css_cache = {}

    # get the list of custom emoji, for use by the mastodon api
    httpd.custom_emoji = \
        metadata_custom_emoji(base_dir, http_prefix, httpd.domain_full)

    # whether to enable broch mode, which locks down the instance
    set_broch_mode(base_dir, httpd.domain_full, broch_mode)

    if not os.path.isdir(base_dir + '/accounts/inbox@' + domain):
        print('Creating shared inbox: inbox@' + domain)
        create_shared_inbox(base_dir, 'inbox', domain, port, http_prefix)

    if not os.path.isdir(base_dir + '/accounts/news@' + domain):
        print('Creating news inbox: news@' + domain)
        create_news_inbox(base_dir, domain, port, http_prefix)
        set_config_param(base_dir, "listsEnabled", "Murdoch press")

    # dict of known web crawlers accessing nodeinfo or the masto API
    # and how many times they have been seen
    httpd.known_crawlers = {}
    known_crawlers_filename = base_dir + '/accounts/knownCrawlers.json'
    if os.path.isfile(known_crawlers_filename):
        httpd.known_crawlers = load_json(known_crawlers_filename)
    # when was the last crawler seen?
    httpd.last_known_crawler = 0

    if lists_enabled:
        httpd.lists_enabled = lists_enabled
    else:
        httpd.lists_enabled = get_config_param(base_dir, "listsEnabled")
    httpd.cw_lists = load_cw_lists(base_dir, True)

    # set the avatar for the news account
    httpd.theme_name = get_config_param(base_dir, 'theme')
    if not httpd.theme_name:
        httpd.theme_name = 'default'
    if is_news_theme_name(base_dir, httpd.theme_name):
        news_instance = True

    httpd.news_instance = news_instance
    httpd.default_timeline = 'inbox'
    if media_instance:
        httpd.default_timeline = 'tlmedia'
    if blogs_instance:
        httpd.default_timeline = 'tlblogs'
    if news_instance:
        httpd.default_timeline = 'tlfeatures'

    set_news_avatar(base_dir,
                    httpd.theme_name,
                    http_prefix,
                    domain,
                    httpd.domain_full)

    if not os.path.isdir(base_dir + '/cache'):
        os.mkdir(base_dir + '/cache')
    if not os.path.isdir(base_dir + '/cache/actors'):
        print('Creating actors cache')
        os.mkdir(base_dir + '/cache/actors')
    if not os.path.isdir(base_dir + '/cache/announce'):
        print('Creating announce cache')
        os.mkdir(base_dir + '/cache/announce')
    if not os.path.isdir(base_dir + '/cache/avatars'):
        print('Creating avatars cache')
        os.mkdir(base_dir + '/cache/avatars')

    archive_dir = base_dir + '/archive'
    if not os.path.isdir(archive_dir):
        print('Creating archive')
        os.mkdir(archive_dir)

    if not os.path.isdir(base_dir + '/sharefiles'):
        print('Creating shared item files directory')
        os.mkdir(base_dir + '/sharefiles')

    print('Creating fitness thread')
    httpd.thrFitness = \
        thread_with_trace(target=fitness_thread,
                          args=(base_dir, httpd.fitness), daemon=True)
    httpd.thrFitness.start()

    print('Creating cache expiry thread')
    httpd.thrCache = \
        thread_with_trace(target=expire_cache,
                          args=(base_dir, httpd.person_cache,
                                httpd.http_prefix,
                                archive_dir,
                                httpd.maxPostsInBox), daemon=True)
    httpd.thrCache.start()

    # number of mins after which sending posts or updates will expire
    httpd.send_threads_timeout_mins = send_threads_timeout_mins

    print('Creating posts queue')
    httpd.thrPostsQueue = \
        thread_with_trace(target=run_posts_queue,
                          args=(base_dir, httpd.send_threads, debug,
                                httpd.send_threads_timeout_mins), daemon=True)
    if not unit_test:
        httpd.thrPostsWatchdog = \
            thread_with_trace(target=run_posts_watchdog,
                              args=(project_version, httpd), daemon=True)
        httpd.thrPostsWatchdog.start()
    else:
        httpd.thrPostsQueue.start()

    print('Creating expire thread for shared items')
    httpd.thrSharesExpire = \
        thread_with_trace(target=run_shares_expire,
                          args=(project_version, base_dir), daemon=True)
    if not unit_test:
        httpd.thrSharesExpireWatchdog = \
            thread_with_trace(target=run_shares_expire_watchdog,
                              args=(project_version, httpd), daemon=True)
        httpd.thrSharesExpireWatchdog.start()
    else:
        httpd.thrSharesExpire.start()

    httpd.recent_posts_cache = {}
    httpd.max_recent_posts = max_recent_posts
    httpd.iconsCache = {}
    httpd.fontsCache = {}

    # create tokens used for shared item federation
    fed_domains = httpd.shared_items_federated_domains
    httpd.shared_item_federation_tokens = \
        generate_shared_item_federation_tokens(fed_domains,
                                               base_dir)
    si_federation_tokens = httpd.shared_item_federation_tokens
    httpd.shared_item_federation_tokens = \
        create_shared_item_federation_token(base_dir, httpd.domain_full, False,
                                            si_federation_tokens)

    # load peertube instances from file into a list
    httpd.peertube_instances = []
    load_peertube_instances(base_dir, httpd.peertube_instances)

    create_initial_last_seen(base_dir, http_prefix)

    print('Creating inbox queue')
    httpd.thrInboxQueue = \
        thread_with_trace(target=run_inbox_queue,
                          args=(httpd.recent_posts_cache,
                                httpd.max_recent_posts,
                                project_version,
                                base_dir, http_prefix, httpd.send_threads,
                                httpd.postLog, httpd.cached_webfingers,
                                httpd.person_cache, httpd.inbox_queue,
                                domain, onion_domain, i2p_domain,
                                port, proxy_type,
                                httpd.federation_list,
                                max_replies,
                                domain_max_posts_per_day,
                                account_max_posts_per_day,
                                allow_deletion, debug,
                                max_mentions, max_emoji,
                                httpd.translate, unit_test,
                                httpd.yt_replace_domain,
                                httpd.twitter_replacement_domain,
                                httpd.show_published_date_only,
                                httpd.max_followers,
                                httpd.allow_local_network_access,
                                httpd.peertube_instances,
                                verify_all_signatures,
                                httpd.theme_name,
                                httpd.system_language,
                                httpd.max_like_count,
                                httpd.signing_priv_key_pem,
                                httpd.default_reply_interval_hrs,
                                httpd.cw_lists), daemon=True)

    print('Creating scheduled post thread')
    httpd.thrPostSchedule = \
        thread_with_trace(target=run_post_schedule,
                          args=(base_dir, httpd, 20), daemon=True)

    print('Creating newswire thread')
    httpd.thrNewswireDaemon = \
        thread_with_trace(target=run_newswire_daemon,
                          args=(base_dir, httpd,
                                http_prefix, domain, port,
                                httpd.translate), daemon=True)

    print('Creating federated shares thread')
    httpd.thrFederatedSharesDaemon = \
        thread_with_trace(target=run_federated_shares_daemon,
                          args=(base_dir, httpd,
                                http_prefix, httpd.domain_full,
                                proxy_type, debug,
                                httpd.system_language), daemon=True)

    # flags used when restarting the inbox queue
    httpd.restart_inbox_queue_in_progress = False
    httpd.restart_inbox_queue = False

    update_hashtag_categories(base_dir)

    print('Adding hashtag categories for language ' + httpd.system_language)
    load_hashtag_categories(base_dir, httpd.system_language)

    # signing key used for authorized fetch
    # this is the instance actor private key
    httpd.signing_priv_key_pem = get_instance_actor_key(base_dir, domain)

    if not unit_test:
        print('Creating inbox queue watchdog')
        httpd.thrWatchdog = \
            thread_with_trace(target=run_inbox_queue_watchdog,
                              args=(project_version, httpd), daemon=True)
        httpd.thrWatchdog.start()

        print('Creating scheduled post watchdog')
        httpd.thrWatchdogSchedule = \
            thread_with_trace(target=run_post_schedule_watchdog,
                              args=(project_version, httpd), daemon=True)
        httpd.thrWatchdogSchedule.start()

        print('Creating newswire watchdog')
        httpd.thrNewswireWatchdog = \
            thread_with_trace(target=run_newswire_watchdog,
                              args=(project_version, httpd), daemon=True)
        httpd.thrNewswireWatchdog.start()

        print('Creating federated shares watchdog')
        httpd.thrFederatedSharesWatchdog = \
            thread_with_trace(target=run_federated_shares_watchdog,
                              args=(project_version, httpd), daemon=True)
        httpd.thrFederatedSharesWatchdog.start()
    else:
        print('Starting inbox queue')
        httpd.thrInboxQueue.start()
        print('Starting scheduled posts daemon')
        httpd.thrPostSchedule.start()
        print('Starting federated shares daemon')
        httpd.thrFederatedSharesDaemon.start()

    if client_to_server:
        print('Running ActivityPub client on ' +
              domain + ' port ' + str(proxy_port))
    else:
        print('Running ActivityPub server on ' +
              domain + ' port ' + str(proxy_port))
    httpd.serve_forever()
