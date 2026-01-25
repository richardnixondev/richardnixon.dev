<?php
/**
 * Plugin Name: Custom Security & Analytics
 * Description: Umami analytics, comment spam protection, login security, and hardening
 * Version: 1.2
 * Author: Richard Nixon
 */

if (!defined('ABSPATH')) {
    exit;
}

// ===========================================
// UMAMI ANALYTICS
// ===========================================
function umami_add_tracking_script() {
    ?>
    <script defer src="https://analytics.richardnixon.dev/script.js" data-website-id="736c63ff-a98d-449a-b0d7-582b3357ffec"></script>
    <?php
}
add_action('wp_head', 'umami_add_tracking_script');

// ===========================================
// COMMENT SECURITY - Block links in comments
// ===========================================
function block_comment_links($commentdata) {
    $comment_content = $commentdata['comment_content'];

    // Check for URLs (http, https, www, or common TLDs)
    $url_patterns = array(
        '/https?:\/\//i',
        '/www\./i',
        '/\[url/i',
        '/href\s*=/i',
        '/\.com\b/i',
        '/\.net\b/i',
        '/\.org\b/i',
        '/\.io\b/i',
        '/\.co\b/i',
        '/\.ru\b/i',
        '/\.cn\b/i',
    );

    foreach ($url_patterns as $pattern) {
        if (preg_match($pattern, $comment_content)) {
            wp_die(
                __('Links are not allowed in comments.', 'umami-security'),
                __('Comment Blocked', 'umami-security'),
                array('response' => 403, 'back_link' => true)
            );
        }
    }

    // Also check the author URL field
    if (!empty($commentdata['comment_author_url'])) {
        $commentdata['comment_author_url'] = '';
    }

    return $commentdata;
}
add_filter('preprocess_comment', 'block_comment_links');

// ===========================================
// ADDITIONAL SPAM PROTECTION
// ===========================================

// Block comments with too many capital letters (shouting = spam)
function block_excessive_caps($commentdata) {
    $content = $commentdata['comment_content'];
    $caps = preg_match_all('/[A-Z]/', $content, $matches);
    $total = strlen(preg_replace('/\s/', '', $content));

    if ($total > 10 && ($caps / $total) > 0.7) {
        wp_die(
            __('Please avoid excessive capital letters.', 'umami-security'),
            __('Comment Blocked', 'umami-security'),
            array('response' => 403, 'back_link' => true)
        );
    }

    return $commentdata;
}
add_filter('preprocess_comment', 'block_excessive_caps');

// Honeypot field - bots fill hidden fields
function add_honeypot_field() {
    echo '<p style="display:none !important;"><label>Leave empty: <input type="text" name="website_url_hp" value="" autocomplete="off" /></label></p>';
}
add_action('comment_form', 'add_honeypot_field');

function check_honeypot_field($commentdata) {
    if (!empty($_POST['website_url_hp'])) {
        wp_die(
            __('Spam detected.', 'umami-security'),
            __('Comment Blocked', 'umami-security'),
            array('response' => 403)
        );
    }
    return $commentdata;
}
add_filter('preprocess_comment', 'check_honeypot_field');

// Block very short comments (likely spam)
function block_short_comments($commentdata) {
    $content = trim($commentdata['comment_content']);
    if (strlen($content) < 10) {
        wp_die(
            __('Comment is too short. Please write at least 10 characters.', 'umami-security'),
            __('Comment Blocked', 'umami-security'),
            array('response' => 403, 'back_link' => true)
        );
    }
    return $commentdata;
}
add_filter('preprocess_comment', 'block_short_comments');

// Block comments with Cyrillic or Chinese characters (common spam)
function block_foreign_characters($commentdata) {
    $content = $commentdata['comment_content'];

    // Block Cyrillic
    if (preg_match('/[\x{0400}-\x{04FF}]/u', $content)) {
        wp_die(
            __('This character set is not allowed.', 'umami-security'),
            __('Comment Blocked', 'umami-security'),
            array('response' => 403, 'back_link' => true)
        );
    }

    // Block Chinese
    if (preg_match('/[\x{4e00}-\x{9fff}]/u', $content)) {
        wp_die(
            __('This character set is not allowed.', 'umami-security'),
            __('Comment Blocked', 'umami-security'),
            array('response' => 403, 'back_link' => true)
        );
    }

    return $commentdata;
}
add_filter('preprocess_comment', 'block_foreign_characters');

// ===========================================
// SECURITY HEADERS
// ===========================================
function add_security_headers() {
    if (!is_admin()) {
        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: SAMEORIGIN');
        header('X-XSS-Protection: 1; mode=block');
        header('Referrer-Policy: strict-origin-when-cross-origin');
    }
}
add_action('send_headers', 'add_security_headers');

// ===========================================
// DISABLE XML-RPC (common attack vector)
// ===========================================
add_filter('xmlrpc_enabled', '__return_false');

// Remove XML-RPC from headers
remove_action('wp_head', 'rsd_link');
remove_action('wp_head', 'wlwmanifest_link');

// ===========================================
// HIDE WORDPRESS VERSION
// ===========================================
remove_action('wp_head', 'wp_generator');

function remove_version_from_scripts($src) {
    if (strpos($src, 'ver=')) {
        $src = remove_query_arg('ver', $src);
    }
    return $src;
}
add_filter('style_loader_src', 'remove_version_from_scripts', 9999);
add_filter('script_loader_src', 'remove_version_from_scripts', 9999);

// ===========================================
// DISABLE FILE EDITING IN ADMIN
// ===========================================
if (!defined('DISALLOW_FILE_EDIT')) {
    define('DISALLOW_FILE_EDIT', true);
}

// ===========================================
// LIMIT LOGIN ATTEMPTS (basic)
// ===========================================
function limit_login_attempts() {
    $ip = $_SERVER['REMOTE_ADDR'];
    $transient_name = 'login_attempts_' . md5($ip);
    $attempts = get_transient($transient_name);

    if ($attempts === false) {
        $attempts = 0;
    }

    if ($attempts >= 5) {
        wp_die(
            __('Too many login attempts. Please try again in 15 minutes.', 'umami-security'),
            __('Access Denied', 'umami-security'),
            array('response' => 429)
        );
    }
}
add_action('wp_login_failed', function() {
    $ip = $_SERVER['REMOTE_ADDR'];
    $transient_name = 'login_attempts_' . md5($ip);
    $attempts = get_transient($transient_name);

    if ($attempts === false) {
        $attempts = 0;
    }

    set_transient($transient_name, $attempts + 1, 15 * MINUTE_IN_SECONDS);
});
add_action('wp_authenticate', 'limit_login_attempts');

// ===========================================
// BLOCK USER ENUMERATION
// ===========================================

// Block REST API user endpoint for non-logged users
function disable_rest_api_users($endpoints) {
    if (!is_user_logged_in()) {
        if (isset($endpoints['/wp/v2/users'])) {
            unset($endpoints['/wp/v2/users']);
        }
        if (isset($endpoints['/wp/v2/users/(?P<id>[\d]+)'])) {
            unset($endpoints['/wp/v2/users/(?P<id>[\d]+)']);
        }
    }
    return $endpoints;
}
add_filter('rest_endpoints', 'disable_rest_api_users');

// Block author archives for non-logged users
function block_author_enumeration() {
    if (is_author() && !is_user_logged_in()) {
        wp_redirect(home_url(), 301);
        exit;
    }
}
add_action('template_redirect', 'block_author_enumeration');

// Block ?author=N queries
function block_author_query() {
    if (!is_user_logged_in() && isset($_GET['author'])) {
        wp_redirect(home_url(), 301);
        exit;
    }
}
add_action('init', 'block_author_query');

// ===========================================
// HIDE SENSITIVE FILES
// ===========================================

// Block access to readme.html, license.txt
function block_sensitive_files() {
    $request_uri = $_SERVER['REQUEST_URI'];
    $blocked_files = array(
        '/readme.html',
        '/license.txt',
        '/wp-config-sample.php',
    );

    foreach ($blocked_files as $file) {
        if (stripos($request_uri, $file) !== false) {
            status_header(404);
            nocache_headers();
            include(get_query_template('404'));
            exit;
        }
    }
}
add_action('init', 'block_sensitive_files', 1);

// ===========================================
// DISABLE REST API FOR NON-AUTHENTICATED (optional - strict mode)
// ===========================================

// Require authentication for REST API (except for specific public endpoints)
function restrict_rest_api($result) {
    if (!is_user_logged_in()) {
        $allowed_routes = array(
            '/oembed/',
            '/contact-form-7/',
        );

        $request_uri = $_SERVER['REQUEST_URI'];

        foreach ($allowed_routes as $route) {
            if (strpos($request_uri, $route) !== false) {
                return $result;
            }
        }

        // Allow only GET requests to specific public data
        if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
            return new WP_Error(
                'rest_forbidden',
                __('REST API restricted to authenticated users.', 'umami-security'),
                array('status' => 401)
            );
        }
    }

    return $result;
}
add_filter('rest_authentication_errors', 'restrict_rest_api');

// ===========================================
// DISABLE PINGBACKS (spam vector)
// ===========================================
add_filter('pings_open', '__return_false', 20, 2);
add_filter('wp_headers', function($headers) {
    unset($headers['X-Pingback']);
    return $headers;
});
