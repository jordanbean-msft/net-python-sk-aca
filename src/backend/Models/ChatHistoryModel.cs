using System.Text.Json.Serialization;

namespace Backend.Models;

public class ChatHistoryModel
{
  [JsonPropertyName("messages")]
  public List<ChatMessage> Messages { get; set; } = new();
}
