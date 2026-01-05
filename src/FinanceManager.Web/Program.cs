using Microsoft.EntityFrameworkCore;
using FinanceManager.Web.Data;

var builder = WebApplication.CreateBuilder(args);

// ========== 加载配置文件 ==========
// 配置文件在 config 目录下
builder.Configuration
    .SetBasePath(builder.Environment.ContentRootPath)
    .AddJsonFile("config/appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"config/appsettings.{builder.Environment.EnvironmentName}.json", optional: true, reloadOnChange: true);

// ========== 1. 添加数据库服务 ==========
// 从appsettings.json读取连接字符串
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
Console.WriteLine($"数据库连接字符串: {connectionString}");
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(connectionString));

// ========== 2. 添加控制器服务 ==========
builder.Services.AddControllers();

// ========== 3. 添加Swagger文档 ==========
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// ========== 4. 添加CORS跨域支持 (让Vue前端能访问) ==========
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowVue", policy =>
    {
        policy.WithOrigins("http://localhost:5173", "http://localhost:3000")  // Vue开发服务器地址
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

var app = builder.Build();

// ========== 5. 自动应用数据库迁移 ==========
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    context.Database.Migrate(); // 应用所有待执行的迁移，这会创建数据库文件
}

app.UseCors("AllowVue");

// ========== 配置中间件管道 ==========
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// 映射控制器路由
app.MapControllers();

// 测试接口：检查数据库是否正常
app.MapGet("/api/health", async (AppDbContext db) =>
{
    var userCount = await db.Users.CountAsync();
    return Results.Ok(new 
    { 
        status = "healthy",
        database = "connected",
        userCount = userCount,
        timestamp = DateTime.UtcNow
    });
});

app.Run();
