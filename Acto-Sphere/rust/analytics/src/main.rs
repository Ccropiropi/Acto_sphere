use futures::StreamExt;
use redis::AsyncCommands;
use serde::{Deserialize, Serialize};
use sqlx::postgres::PgPoolOptions;
use std::env;

#[derive(Serialize, Deserialize, Debug)]
struct LogEntry {
    timestamp: String,
    file: String,
    change: String,
}

#[derive(Serialize, Debug)]
struct DashboardStats {
    frequent_analytics: std::collections::HashMap<String, i64>,
    total_events: i64,
    last_updated: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Starting Rust Analytics Engine...");

    // 1. Connect to Postgres
    let db_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&db_url)
        .await?;

    // Create Table if not exists
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS file_events (
            id SERIAL PRIMARY KEY,
            timestamp TEXT,
            filename TEXT,
            change_type TEXT
        );
        "#,
    )
    .execute(&pool)
    .await?;

    // 2. Connect to Redis
    let redis_url = env::var("REDIS_URL").expect("REDIS_URL must be set");
    let client = redis::Client::open(redis_url)?;
    let mut pubsub_conn = client.get_async_connection().await?.into_pubsub();
    let mut cache_conn = client.get_async_connection().await?;

    pubsub_conn.subscribe("file_events").await?;
    let mut stream = pubsub_conn.on_message();

    println!("Listening for events...");

    while let Some(msg) = stream.next().await {
        let payload: String = msg.get_payload()?;
        
        // Process Event (Simulating High Performance Logic)
        if let Ok(entry) = serde_json::from_str::<LogEntry>(&payload) {
            // A. Insert into DB (Async)
            let _ = sqlx::query!(
                "INSERT INTO file_events (timestamp, filename, change_type) VALUES ($1, $2, $3)",
                entry.timestamp,
                entry.file,
                entry.change
            )
            .execute(&pool)
            .await;

            // B. Calculate Aggregates (Simplified for demo)
            // In a real app, you might do this periodically or incrementally
            let rows = sqlx::query!("SELECT filename FROM file_events")
                .fetch_all(&pool)
                .await?;

            let mut counts = std::collections::HashMap::new();
            for row in &rows {
                if let Some(ext) = std::path::Path::new(&row.filename.unwrap_or_default()).extension() {
                   *counts.entry(format!(".{}", ext.to_string_lossy())).or_insert(0) += 1;
                }
            }

            // C. Update Cache
            let stats = DashboardStats {
                frequent_analytics: counts,
                total_events: rows.len() as i64,
                last_updated: chrono::Local::now().to_rfc3339(),
            };

            let json_stats = serde_json::to_string(&stats)?;
            let _: () = cache_conn.set("dashboard_stats", json_stats).await?;
            
            // println!("Cache updated.");
        }
    }

    Ok(())
}
