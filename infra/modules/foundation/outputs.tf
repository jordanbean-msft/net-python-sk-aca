output "unique_suffix" {
  description = "Unique suffix for resource naming"
  value       = random_string.unique.result
}
