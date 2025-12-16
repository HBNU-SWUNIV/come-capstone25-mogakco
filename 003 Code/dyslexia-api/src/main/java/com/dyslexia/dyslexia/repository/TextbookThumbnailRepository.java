package com.dyslexia.dyslexia.repository;

import com.dyslexia.dyslexia.entity.TextbookThumbnail;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface TextbookThumbnailRepository extends JpaRepository<TextbookThumbnail, Long> {

    Optional<TextbookThumbnail> findByJobId(String jobId);

    Optional<TextbookThumbnail> findByTextbookId(Long textbookId);

    @Query("SELECT tt FROM TextbookThumbnail tt WHERE tt.textbook.id = :textbookId")
    Optional<TextbookThumbnail> findByTextbook(@Param("textbookId") Long textbookId);

    boolean existsByJobId(String jobId);

    boolean existsByTextbookId(Long textbookId);
}