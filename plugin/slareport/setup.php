<?php

/**
 * Plugin definition and initialization
 */

define('PLUGIN_SLAREPORT_VERSION', '1.0.1');

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

   // Localization Ayarı
   // GLPI eklenti sisteminde 'languages' hook'u gettext veya php tabanlı çeviriyi tetikler
   $PLUGIN_HOOKS['languages']['slareport'] = [
      'type' => 'php', // .php dosyaları kullandığın için 'php' olmalı
      'domain' => 'slareport'
   ];

}

/**
 * Get the name and the version of the plugin
 */
function plugin_version_slareport()
{
   return [
      'name' => __('SLA Breach Report', 'slareport'),
      'version' => PLUGIN_SLAREPORT_VERSION,
      'author' => 'Bora Ergül',
      'license' => 'GPLv2+',
      'homepage' => '',
      'requirements' => [
         'glpi' => [
            'min' => '10.0',
            'max' => '12.0',
         ]
      ]
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
 * Check if the plugin is compatible with the version of GLPI
 */
function plugin_slareport_check_config()
{
   return true;
}
