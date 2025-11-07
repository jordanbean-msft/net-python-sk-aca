using System.Text.Json.Serialization;

namespace Backend.Models;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum MessageRole
{
  System,
  User,
  Assistant
}
