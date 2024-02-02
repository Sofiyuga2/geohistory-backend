package models

type CheckArchiveRequest struct {
	AccessToken      int64 `json:"access_key"`
	Checking_archive int   `json:"verify"`
}
