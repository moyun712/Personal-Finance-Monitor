using Microsoft.EntityFrameworkCore;
using FinanceManager.Web.Models;

namespace FinanceManager.Web.Data;

/// <summary>
/// 数据库上下文 (这是EF Core的核心，管理所有数据库操作)
/// </summary>
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }

    /// <summary>
    /// 用户表
    /// </summary>
    public DbSet<User> Users { get; set; }

    /// <summary>
    /// AI使用记录表
    /// </summary>
    public DbSet<AIUsageLog> AIUsageLogs { get; set; }

    /// <summary>
    /// 配置数据库模型 (设置索引、关系等)
    /// </summary>
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // 配置User表
        modelBuilder.Entity<User>(entity =>
        {
            // 用户名必须唯一
            entity.HasIndex(u => u.Username).IsUnique();
            
            // 邮箱必须唯一
            entity.HasIndex(u => u.Email).IsUnique();
            
            // Username和Email不能为空
            entity.Property(u => u.Username).IsRequired().HasMaxLength(50);
            entity.Property(u => u.Email).IsRequired().HasMaxLength(100);
            entity.Property(u => u.PasswordHash).IsRequired();
        });

        // 配置AIUsageLog表
        modelBuilder.Entity<AIUsageLog>(entity =>
        {
            // 设置外键关系: 一个用户可以有多条使用记录
            entity.HasOne(log => log.User)
                .WithMany()  // User端不需要导航属性
                .HasForeignKey(log => log.UserId)
                .OnDelete(DeleteBehavior.Cascade);  // 删除用户时，自动删除相关记录

            entity.Property(log => log.FunctionType).IsRequired().HasMaxLength(20);
            entity.Property(log => log.Status).IsRequired().HasMaxLength(20);
            
            // 为UserId和CreatedAt创建索引（加速查询）
            entity.HasIndex(log => log.UserId);
            entity.HasIndex(log => log.CreatedAt);
        });
    }
}
