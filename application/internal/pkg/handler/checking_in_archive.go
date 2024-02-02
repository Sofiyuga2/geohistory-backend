package handler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"lab8/internal/models"
	"math/rand"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func (h *Handler) issueCheckArchive(c *gin.Context) {
	var input models.Request
	if err := c.BindJSON(&input); err != nil {
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}
	fmt.Println("handler.issueCheckArchive:", input)

	c.Status(http.StatusOK)

	go func() {
		time.Sleep(5 * time.Second)
		sendCheckingArchiveRequest(input)
	}()
}

func sendCheckingArchiveRequest(request models.Request) {

	var check = 0
	if rand.Intn(10)%10 >= 3 {
		check = rand.Intn(2)
	}
	fmt.Println("check:", check)
	answer := models.CheckArchiveRequest{
		AccessToken:      123,
		Checking_archive: check,
	}
	fmt.Println("check:", check)
	client := &http.Client{}

	jsonAnswer, _ := json.Marshal(answer)
	bodyReader := bytes.NewReader(jsonAnswer)

	requestURL := fmt.Sprintf("http://127.0.0.1:8000/api/discoveries/%d/checking_in_archive/", request.DiscoveriesId)

	req, _ := http.NewRequest(http.MethodPut, requestURL, bodyReader)

	req.Header.Set("Content-Type", "application/json")

	response, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending PUT request:", err)
		return
	}

	defer response.Body.Close()

	fmt.Println("PUT Request Status:", response.Status)
}
