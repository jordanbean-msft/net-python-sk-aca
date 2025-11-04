using Backend.Models;
using Microsoft.AspNetCore.Mvc;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace Backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
  private readonly IHttpClientFactory _httpClientFactory;
  private readonly ILogger<ChatController> _logger;
  private readonly JsonSerializerOptions _jsonOptions;

  public ChatController(IHttpClientFactory httpClientFactory, ILogger<ChatController> logger)
  {
    _httpClientFactory = httpClientFactory;
    _logger = logger;
    _jsonOptions = new JsonSerializerOptions
    {
      PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
      WriteIndented = false
    };
  }

  [HttpPost]
  public async Task<IActionResult> Chat([FromBody] ChatRequest request, CancellationToken cancellationToken)
  {
    try
    {
      if (string.IsNullOrWhiteSpace(request.Message))
      {
        return BadRequest(new { error = "Message is required" });
      }

      var httpClient = _httpClientFactory.CreateClient("PythonApi");

      // Serialize request
      var jsonContent = JsonSerializer.Serialize(request, _jsonOptions);
      var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

      _logger.LogInformation("Sending chat request to Python API: {Message}", request.Message);

      // Make request to Python API
      var response = await httpClient.PostAsync("/api/chat", content, cancellationToken);

      if (!response.IsSuccessStatusCode)
      {
        var errorContent = await response.Content.ReadAsStringAsync(cancellationToken);
        _logger.LogError("Python API returned error: {StatusCode} - {Error}",
            response.StatusCode, errorContent);
        return StatusCode((int)response.StatusCode, new { error = errorContent });
      }

      // If streaming is requested
      if (request.Stream)
      {
        Response.Headers["Content-Type"] = "text/event-stream";
        Response.Headers["Cache-Control"] = "no-cache";
        Response.Headers["Connection"] = "keep-alive";

        var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
        using var reader = new StreamReader(stream);

        await Response.StartAsync(cancellationToken);

        while (!reader.EndOfStream && !cancellationToken.IsCancellationRequested)
        {
          var line = await reader.ReadLineAsync(cancellationToken);
          if (!string.IsNullOrEmpty(line))
          {
            await Response.WriteAsync(line + "\n", cancellationToken);
            await Response.Body.FlushAsync(cancellationToken);
          }
        }

        await Response.CompleteAsync();
        return new EmptyResult();
      }
      else
      {
        // Non-streaming response
        var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);
        var chatResponse = JsonSerializer.Deserialize<ChatResponse>(responseContent, _jsonOptions);
        return Ok(chatResponse);
      }
    }
    catch (HttpRequestException ex)
    {
      _logger.LogError(ex, "Failed to connect to Python API");
      return StatusCode(503, new { error = "Failed to connect to AI service" });
    }
    catch (Exception ex)
    {
      _logger.LogError(ex, "Error processing chat request");
      return StatusCode(500, new { error = "Internal server error" });
    }
  }
}
