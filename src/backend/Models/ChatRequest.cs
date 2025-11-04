using System.Text.Json.Serialization;

namespace Backend.Models;

public class ChatRequest
{
  [JsonPropertyName("message")]
  public string Message { get; set; } = string.Empty;

  [JsonPropertyName("history")]
  public ChatHistoryModel? History { get; set; }

  [JsonPropertyName("stream")]
  public bool Stream { get; set; } = true;
}
