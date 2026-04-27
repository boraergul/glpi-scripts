<?php

define('PLUGIN_SLAREPORT_VERSION', '1.2.2');

/**
 * Safe translation for setup.php (avoids Class Not Found error)
 */
function slareport_get_title_safe() {
    $lang = $_SESSION['glpilanguage'] ?? 'en_GB';
    return ($lang == 'tr_TR') ? 'SLA İhlal Raporu' : 'SLA Breach Report';
}

/**
 * Init function for the plugin
 */
function plugin_init_slareport()
{
    global $PLUGIN_HOOKS;

    $PLUGIN_HOOKS['csrf_compliant']['slareport'] = true;

    $PLUGIN_HOOKS['menu_toadd']['slareport'] = [
        'tools' => 'PluginSlareportReport'
    ];

    if (Session::haveRight("config", 1)) {
        $PLUGIN_HOOKS['config_page']['slareport'] = 'front/index.php';
    }

    $PLUGIN_HOOKS['languages']['slareport'] = [
        'type' => 'php',
        'domain' => 'slareport'
    ];
}

/**
 * Get the name and the version of the plugin
 */
function plugin_version_slareport()
{
    return [
        'name'           => slareport_get_title_safe(),
        'version'        => PLUGIN_SLAREPORT_VERSION,
        'author'         => 'Bora Ergül',
        'license'        => 'GPLv2+',
        'homepage'       => '',
        'minGlpiVersion' => '10.0'
    ];
}

/**
 * Check pre-requisites for the plugin
 */
function plugin_slareport_check_prerequisites()
{
    return true;
}

/**
 * Check configuration for the plugin
 */
function plugin_slareport_check_config()
{
    return true;
}
