package com.mentalhealth.assistant.model;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "mood_logs",
       uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "log_date"}))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MoodLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "log_date", nullable = false)
    private LocalDate logDate;

    @Column(name = "mood_score", nullable = false)
    private Integer moodScore;  // 1-10 scale

    @Enumerated(EnumType.STRING)
    @Column(name = "mood_label", nullable = false)
    private MoodLabel moodLabel;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Enumerated(EnumType.STRING)
    @Column(name = "primary_emotion")
    private ChatMessage.EmotionType primaryEmotion;

    @Column(name = "sleep_hours")
    private Double sleepHours;

    @Column(name = "anxiety_level")
    private Integer anxietyLevel;  // 1-10

    @Column(name = "stress_level")
    private Integer stressLevel;   // 1-10

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public enum MoodLabel {
        VERY_BAD, BAD, NEUTRAL, GOOD, VERY_GOOD
    }
}
