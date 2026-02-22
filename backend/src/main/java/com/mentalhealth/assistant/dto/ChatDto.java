package com.mentalhealth.assistant.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

public class ChatDto {

    @Data
    public static class SendMessageRequest {
        @NotBlank(message = "Message content cannot be empty")
        @Size(max = 4000, message = "Message too long")
        private String content;
        private Long sessionId;  // null = new session
    }

    @Data
    @Builder
    public static class MessageResponse {
        private Long id;
        private String role;
        private String content;
        private String detectedEmotion;
        private Double emotionScore;
        private boolean isEmergency;
        private LocalDateTime createdAt;
    }

    @Data
    @Builder
    public static class ChatResponse {
        private Long sessionId;
        private String sessionTitle;
        private MessageResponse userMessage;
        private MessageResponse assistantMessage;
        private boolean emergencyDetected;
        private EmergencyInfo emergencyInfo;
    }

    @Data
    @Builder
    public static class EmergencyInfo {
        private String message;
        private String hotlineVN;
        private String hotlineEN;
        private String website;
        private List<String> resources;
    }

    @Data
    @Builder
    public static class SessionResponse {
        private Long id;
        private String title;
        private boolean isActive;
        private String sessionStatus;
        private boolean emergencyTriggered;
        private LocalDateTime createdAt;
        private LocalDateTime updatedAt;
        private Integer messageCount;
    }

    @Data
    @Builder
    public static class SessionDetailResponse {
        private Long id;
        private String title;
        private String sessionStatus;
        private boolean emergencyTriggered;
        private LocalDateTime createdAt;
        private List<MessageResponse> messages;
    }
}
