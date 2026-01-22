FROM golang:1.21-alpine

WORKDIR /app
COPY go.mod ./
# Only fetch dependencies if go.sum exists (simplified for now)
# RUN go mod download 

COPY main.go .
# Create a dummy go.sum to satisfy build if needed, or run tidy
RUN go mod tidy
RUN go build -o ingestor main.go

CMD ["./ingestor"]
