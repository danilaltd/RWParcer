using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RWParcer.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Sessions",
                columns: table => new
                {
                    ChatId = table.Column<string>(type: "text", nullable: false),
                    CurrentCommand = table.Column<int>(type: "integer", nullable: true),
                    InitState = table.Column<bool>(type: "boolean", nullable: false),
                    Data = table.Column<string>(type: "TEXT", nullable: false),
                    Date = table.Column<DateOnly>(type: "date", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Sessions", x => x.ChatId);
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Sessions");
        }
    }
}
