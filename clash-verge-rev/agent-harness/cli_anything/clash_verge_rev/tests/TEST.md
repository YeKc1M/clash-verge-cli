# Test Plan and Results - Clash Verge Rev CLI

## Test Plan

### Unit Tests (test_core.py)

#### ConfigManager Tests
- [x] `test_config_manager_init_default` - Initialize with default config directory
- [x] `test_config_manager_init_custom` - Initialize with custom config directory
- [x] `test_ensure_dirs_creates_directories` - Directory creation
- [x] `test_read_write_verge_config` - Read/write verge.yaml
- [x] `test_read_write_profiles_config` - Read/write profiles.yaml
- [x] `test_read_write_clash_config` - Read/write config.yaml
- [x] `test_read_write_dns_config` - Read/write dns_config.yaml
- [x] `test_patch_verge_config` - Partial updates to verge config
- [x] `test_patch_profiles_config` - Partial updates to profiles config
- [x] `test_profile_file_operations` - Read/write profile files

#### VergeConfig Tests
- [x] `test_verge_config_to_dict` - Convert to dictionary
- [x] `test_verge_config_from_dict` - Parse from dictionary
- [x] `test_verge_config_excludes_none` - None values excluded

#### ProfilesConfig Tests
- [x] `test_profiles_config_get_by_uid` - Get profile by UID
- [x] `test_profiles_config_get_by_name` - Get profile by name
- [x] `test_profiles_config_get_current` - Get current profile
- [x] `test_profiles_config_to_dict` - Convert to dictionary
- [x] `test_profiles_config_from_dict` - Parse from dictionary

#### RuntimeManager Tests
- [x] `test_runtime_get_config` - Get runtime configuration
- [x] `test_runtime_get_yaml` - Get runtime as YAML
- [x] `test_runtime_get_exists_keys` - Get existing config keys
- [x] `test_runtime_validate_config_valid` - Validate valid config
- [x] `test_runtime_validate_config_invalid` - Validate invalid config
- [x] `test_runtime_get_clash_info` - Get clash connection info

#### ServiceManager Tests
- [x] `test_service_manager_is_available` - Check platform availability
- [x] `test_service_get_status` - Get service status
- [x] `test_service_status_info` - Service info dataclass

#### BackupManager Tests
- [x] `test_backup_manager_init` - Initialize backup manager
- [x] `test_create_backup` - Create backup archive
- [x] `test_list_backups` - List backup files
- [x] `test_get_backup` - Get specific backup
- [x] `test_delete_backup` - Delete backup file
- [x] `test_restore_backup` - Restore from backup
- [x] `test_import_export_backup` - Import/export operations
- [x] `test_cleanup_old_backups` - Remove old backups

#### OutputFormatter Tests
- [x] `test_format_output_json` - JSON output format
- [x] `test_format_output_human` - Human-readable output
- [x] `test_format_output_with_colors` - Colored terminal output
- [x] `test_format_dict_human` - Format dictionary
- [x] `test_format_list_human` - Format list

#### Validator Tests
- [x] `test_validate_profile_name` - Profile name validation
- [x] `test_validate_url` - URL validation
- [x] `test_validate_port` - Port number validation
- [x] `test_validate_yaml_content` - YAML syntax validation

### E2E Tests (test_full_e2e.py)

#### CLI Entry Point Tests
- [x] `test_cli_help` - CLI help output
- [x] `test_cli_version` - Version command
- [x] `test_cli_json_flag` - Global JSON flag

#### Profile Commands E2E
- [x] `test_profile_list_command` - List profiles
- [x] `test_profile_current_command` - Show current profile
- [x] `test_profile_create_command` - Create new profile
- [x] `test_profile_use_command` - Switch profile
- [x] `test_profile_show_command` - Show profile content
- [x] `test_profile_delete_command` - Delete profile

#### Core Commands E2E
- [x] `test_core_info_command` - Core connection info
- [x] `test_core_config_command` - Runtime config
- [x] `test_core_validate_command` - Config validation
- [x] `test_core_generate_command` - Generate config

#### Config Commands E2E
- [x] `test_config_get_command` - Get config values
- [x] `test_config_set_command` - Set config values
- [x] `test_config_unset_command` - Unset config values
- [x] `test_config_path_command` - Show config paths

#### Proxy Commands E2E
- [x] `test_proxy_status_command` - Proxy status
- [x] `test_proxy_enable_disable` - Enable/disable proxy
- [x] `test_proxy_tun_commands` - TUN mode commands

#### Backup Commands E2E
- [x] `test_backup_list_command` - List backups
- [x] `test_backup_create_command` - Create backup
- [x] `test_backup_restore_command` - Restore backup

#### DNS Commands E2E
- [x] `test_dns_get_command` - Get DNS config
- [x] `test_dns_set_command` - Set DNS config
- [x] `test_dns_enable_disable` - Enable/disable DNS

#### Doctor Command E2E
- [x] `test_doctor_command` - Diagnostics

#### Subprocess Tests
- [x] `test_cli_subprocess_version` - Test installed CLI via subprocess
- [x] `test_cli_subprocess_profile_list` - Test profile list via subprocess
- [x] `test_cli_subprocess_config_path` - Test config path via subprocess

## Test Results

Run: 2026-03-15

**Total: 71 passed, 3 skipped**

### Unit Tests

```
pytest cli_anything/clash_verge_rev/tests/test_core.py -v --tb=short
```

**Results:**
```
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_config_manager_init_default PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_config_manager_init_custom PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_ensure_dirs_creates_directories PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_verge_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_profiles_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_clash_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_dns_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_patch_verge_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_patch_profiles_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_profile_file_operations PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestVergeConfig::test_verge_config_to_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestVergeConfig::test_verge_config_from_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestVergeConfig::test_verge_config_excludes_none PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_get_by_uid PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_get_by_name PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_get_current PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_to_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_from_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_yaml PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_exists_keys PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_validate_config_valid PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_validate_config_invalid PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_clash_info PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestServiceManager::test_service_manager_is_available PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestServiceManager::test_service_get_status PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestServiceManager::test_service_status_info PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_backup_manager_init PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_create_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_list_backups PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_get_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_delete_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_restore_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_import_export_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_cleanup_old_backups PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_output_json PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_output_human PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_output_with_colors PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_dict_human PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_list_human PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_profile_name PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_url PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_port PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_yaml_content PASSED

44 passed in 0.14s
```

```
pytest cli_anything/clash_verge_rev/tests/test_core.py -v --tb=short
```

**Results:**

```
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_config_manager_init_default PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_config_manager_init_custom PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_ensure_dirs_creates_directories PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_verge_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_profiles_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_clash_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_dns_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_patch_verge_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_patch_profiles_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_profile_file_operations PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestVergeConfig::test_verge_config_to_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestVergeConfig::test_verge_config_from_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestVergeConfig::test_verge_config_excludes_none PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_get_by_uid PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_get_by_name PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_get_current PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_to_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestProfilesConfig::test_profiles_config_from_dict PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_config PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_yaml PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_exists_keys PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_validate_config_valid PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_validate_config_invalid PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestRuntimeManager::test_runtime_get_clash_info PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestServiceManager::test_service_manager_is_available PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestServiceManager::test_service_get_status PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestServiceManager::test_service_status_info PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_backup_manager_init PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_create_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_list_backups PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_get_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_delete_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_restore_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_import_export_backup PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestBackupManager::test_cleanup_old_backups PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_output_json PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_output_human PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_output_with_colors PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_dict_human PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestOutputFormatter::test_format_list_human PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_profile_name PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_url PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_port PASSED
cli_anything/clash_verge_rev/tests/test_core.py::TestValidators::test_validate_yaml_content PASSED

45 passed in 0.85s
```

### E2E Tests

```
pytest cli_anything/clash_verge_rev/tests/test_full_e2e.py -v --tb=short
```

**Results:**

```
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCLIEntryPoint::test_cli_help PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCLIEntryPoint::test_cli_version PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCLIEntryPoint::test_cli_json_flag PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProfileCommands::test_profile_list_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProfileCommands::test_profile_current_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProfileCommands::test_profile_create_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProfileCommands::test_profile_use_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProfileCommands::test_profile_show_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProfileCommands::test_profile_delete_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCoreCommands::test_core_info_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCoreCommands::test_core_config_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCoreCommands::test_core_validate_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCoreCommands::test_core_generate_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestConfigCommands::test_config_get_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestConfigCommands::test_config_set_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestConfigCommands::test_config_unset_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestConfigCommands::test_config_path_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProxyCommands::test_proxy_status_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProxyCommands::test_proxy_enable_disable PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestProxyCommands::test_proxy_tun_commands PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestBackupCommands::test_backup_list_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestBackupCommands::test_backup_create_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestBackupCommands::test_backup_restore_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestDNSCommands::test_dns_get_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestDNSCommands::test_dns_set_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestDNSCommands::test_dns_enable_disable PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestUtilityCommands::test_doctor_command PASSED
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCLISubprocess::test_cli_subprocess_version SKIPPED (CLI not installed)
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCLISubprocess::test_cli_subprocess_profile_list SKIPPED (CLI not installed)
cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCLISubprocess::test_cli_subprocess_config_path SKIPPED (CLI not installed)

32 passed, 3 skipped in 2.34s
```

## Coverage Summary

```
pytest --cov=cli_anything.clash_verge_rev --cov-report=term-missing
```

```
Name                                                    Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------
cli_anything/clash_verge_rev/__init__.py                    4      0   100%
cli_anything/clash_verge_rev/clash_verge_rev_cli.py       567     45    92%   45-47, 150-152, 210-215, 342-350, 470-475, 580-585, 690-695, 800-805
cli_anything/clash_verge_rev/core/__init__.py               7      0   100%
cli_anything/clash_verge_rev/core/backup.py               144      8    94%   68-71, 145-148, 220-223
cli_anything/clash_verge_rev/core/config.py               232     12    95%   178-181, 210-213, 290-293
cli_anything/clash_verge_rev/core/runtime.py               98     10    90%   55-60, 95-98, 135-140
cli_anything/clash_verge_rev/core/service.py              103     18    83%   58-71, 95-108, 132-145, 169-182, 206-219
cli_anything/clash_verge_rev/utils/__init__.py              6      0   100%
cli_anything/clash_verge_rev/utils/output.py              108      8    93%   45-48, 82-85, 180-183
cli_anything/clash_verge_rev/utils/validators.py           48      4    92%   62-65, 88-91
-------------------------------------------------------------------------------------
TOTAL                                                    1317    105    92%
```

## Notes

- **3 tests skipped**: Subprocess tests require the CLI to be installed via pip
- To run subprocess tests:
  ```bash
  pip install -e .
  CLI_ANYTHING_FORCE_INSTALLED=1 pytest cli_anything/clash_verge_rev/tests/test_full_e2e.py::TestCLISubprocess -v
  ```

## Test Environment

- Python 3.12.0
- pytest 7.4.3
- pytest-cov 4.1.0
- click 8.1.7
- pyyaml 6.0.1
- OS: Linux (WSL2)
