package main

import (
    "log"
    "net/http"

    "github.com/gin-gonic/gin"
)

func main() {
    router := gin.Default()
    
    // Health check endpoint
    router.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "status": "healthy",
        })
    })
    
    // User endpoints
    router.GET("/api/v1/users/:id", getUser)
    router.POST("/api/v1/users", createUser)
    
    log.Fatal(router.Run(":8080"))
}

func getUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{
        "id": id,
        "name": "John Doe",
    })
}

func createUser(c *gin.Context) {
    // Implementation here
    c.JSON(http.StatusCreated, gin.H{
        "message": "User created",
    })
}
