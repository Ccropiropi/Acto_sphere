package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/hpcloud/tail"
)

var ctx = context.Background()

func main() {
	// 1. Connect to Redis
	rdb := redis.NewClient(&redis.Options{
		Addr: "redis:6379",
	})

	// Wait for Redis to be ready
	for {
		if _, err := rdb.Ping(ctx).Result(); err == nil {
			break
		}
		log.Println("Waiting for Redis...")
		time.Sleep(2 * time.Second)
	}
	log.Println("Connected to Redis.")

	// 2. Tail the Log File
	logFile := "/app/dat/changes_log.json"
	t, err := tail.TailFile(logFile, tail.Config{
		Follow: true,
		ReOpen: true,
		Poll:   true, // Needed for Docker mounted volumes sometimes
	})
	if err != nil {
		log.Fatal(err)
	}

	// 3. Publish Loop (Asynchronous)
	for line := range t.Lines {
		// Publish raw JSON line to 'file_events' channel
		err := rdb.Publish(ctx, "file_events", line.Text).Err()
		if err != nil {
			log.Printf("Error publishing: %v", err)
		} else {
			// fmt.Println("Published event to Redis")
		}
	}
}
