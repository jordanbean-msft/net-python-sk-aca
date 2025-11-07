var builder = WebApplication.CreateBuilder(args);

// Configure Kestrel to use PORT from environment variable
var port = builder.Configuration["PORT"] ?? "8080";
builder.WebHost.ConfigureKestrel(serverOptions =>
{
  serverOptions.ListenAnyIP(int.Parse(port));
});

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure HttpClient for Python API
builder.Services.AddHttpClient("PythonApi", client =>
{
  var pythonApiUrl = builder.Configuration["PythonApiUrl"] ?? "http://localhost:8000";
  client.BaseAddress = new Uri(pythonApiUrl);
  client.Timeout = TimeSpan.FromMinutes(5); // Allow long-running streaming requests
});

// Add CORS
builder.Services.AddCors(options =>
{
  options.AddPolicy("AllowAll", policy =>
  {
    policy.AllowAnyOrigin()
            .AllowAnyMethod()
            .AllowAnyHeader();
  });
});

// Add health checks
builder.Services.AddHealthChecks();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
  app.UseSwagger();
  app.UseSwaggerUI();
}

app.UseCors("AllowAll");

app.UseDefaultFiles();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllers();
app.MapHealthChecks("/health");

// Fallback to serve React app for SPA routing
app.MapFallbackToFile("index.html");

app.Run();
