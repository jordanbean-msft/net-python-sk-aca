########## Generic Container App Module ##########

resource "azurerm_container_app" "main" {
  name                         = var.name
  container_app_environment_id = var.environment_id
  resource_group_name          = var.resource_group_name
  revision_mode                = var.revision_mode
  tags                         = var.tags

  identity {
    type         = "UserAssigned"
    identity_ids = var.identity_ids
  }

  registry {
    server   = var.registry_server
    identity = var.registry_identity_id
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = var.name
      image  = var.image
      cpu    = var.cpu
      memory = var.memory

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name        = env.key
          secret_name = env.key
        }
      }

      startup_probe {
        path                    = var.health_probe_path
        port                    = var.target_port
        transport               = "HTTP"
        initial_delay           = var.startup_probe_initial_delay
        timeout                 = var.startup_probe_timeout
        interval_seconds        = var.startup_probe_period
        failure_count_threshold = var.startup_probe_failure_threshold
      }

      liveness_probe {
        path                    = var.health_probe_path
        port                    = var.target_port
        transport               = "HTTP"
        initial_delay           = 5
        timeout                 = 3
        interval_seconds        = 10
        failure_count_threshold = 3
      }

      readiness_probe {
        path                    = var.health_probe_path
        port                    = var.target_port
        transport               = "HTTP"
        initial_delay           = 5
        timeout                 = 3
        interval_seconds        = 10
        failure_count_threshold = 3
        success_count_threshold = 1
      }
    }
  }

  dynamic "secret" {
    for_each = var.secret_env_vars
    content {
      name  = secret.key
      value = secret.value
    }
  }

  ingress {
    external_enabled = var.external_enabled
    target_port      = var.target_port
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  # Do not overwrite runtime image after initial creation; allows external deploys to manage revisions.
  lifecycle {
    ignore_changes = [
      template[0].container[0].image
    ]
  }
}
