package com.dyslexia.dyslexia.service;

import com.dyslexia.dyslexia.dto.ThumbnailCallbackRequestDto;
import com.dyslexia.dyslexia.dto.TextbookThumbnailResponseDto;
import com.dyslexia.dyslexia.entity.Textbook;
import com.dyslexia.dyslexia.entity.TextbookThumbnail;
import com.dyslexia.dyslexia.repository.TextbookRepository;
import com.dyslexia.dyslexia.repository.DocumentRepository;
import com.dyslexia.dyslexia.repository.TextbookThumbnailRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Slf4j
@Service
@RequiredArgsConstructor
public class TextbookThumbnailService {

    private final TextbookThumbnailRepository thumbnailRepository;
    private final TextbookRepository textbookRepository;
    private final DocumentRepository documentRepository;

    @Transactional
    public void handleThumbnailCallback(String jobId, ThumbnailCallbackRequestDto request) {
        log.info("=== 썸네일 콜백 처리 시작 ===");
        log.info("JobId: {}, ThumbnailUrl: {}, PdfName: {}", jobId, request.getThumbnailUrl(), request.getPdfName());

        // JobId 검증
        if (!jobId.equals(request.getJobId())) {
            log.warn("JobId 불일치: PathVariable={}, RequestBody={}", jobId, request.getJobId());
            throw new IllegalArgumentException("JobId가 일치하지 않습니다");
        }

        // 기존 썸네일 정보 조회
        Optional<TextbookThumbnail> existingThumbnail = thumbnailRepository.findByJobId(jobId);

        if (existingThumbnail.isPresent()) {
            // 기존 썸네일 정보 업데이트
            TextbookThumbnail thumbnail = existingThumbnail.get();
            thumbnail.updateThumbnailInfo(
                request.getPdfName(),
                request.getThumbnailUrl(),
                request.getS3Key(),
                request.getWidth(),
                request.getHeight()
            );
            thumbnailRepository.save(thumbnail);
            log.info("기존 썸네일 정보 업데이트 완료: TextbookId={}", thumbnail.getTextbook().getId());
        } else {
            // 썸네일 정보가 없으면 jobId를 통해 문서/교재를 찾아 신규 생성 (upsert)
            log.warn("JobId={}에 해당하는 기존 썸네일 정보가 없어 새로 생성합니다", jobId);

            var documentOpt = documentRepository.findByJobId(jobId);
            if (documentOpt.isEmpty()) {
                log.error("JobId={}에 해당하는 문서를 찾을 수 없습니다", jobId);
                throw new IllegalArgumentException("해당 JobId에 대한 문서를 찾을 수 없습니다");
            }

            var document = documentOpt.get();
            var textbookOpt = textbookRepository.findByDocumentId(document.getId());
            if (textbookOpt.isEmpty()) {
                log.error("문서(id={})에 매핑된 교재를 찾을 수 없습니다 (jobId={})", document.getId(), jobId);
                throw new IllegalArgumentException("해당 문서에 대한 교재가 없습니다");
            }

            Textbook textbook = textbookOpt.get();

            TextbookThumbnail newThumbnail = TextbookThumbnail.builder()
                .textbook(textbook)
                .jobId(jobId)
                .pdfName(request.getPdfName())
                .thumbnailUrl(request.getThumbnailUrl())
                .s3Key(request.getS3Key())
                .width(request.getWidth())
                .height(request.getHeight())
                .build();
            thumbnailRepository.save(newThumbnail);
            log.info("신규 썸네일 정보 생성 완료: TextbookId={}", textbook.getId());
        }

        log.info("썸네일 콜백 처리 완료");
    }

    @Transactional
    public String createThumbnailJob(Long textbookId, String jobId) {
        log.info("썸네일 작업 생성: TextbookId={}, JobId={}", textbookId, jobId);

        // 교재 존재 확인
        Textbook textbook = textbookRepository.findById(textbookId)
            .orElseThrow(() -> new IllegalArgumentException("해당 교재를 찾을 수 없습니다: " + textbookId));

        // 기존 썸네일 정보 확인
        Optional<TextbookThumbnail> existingThumbnail = thumbnailRepository.findByTextbookId(textbookId);

        if (existingThumbnail.isPresent()) {
            // 기존 썸네일 정보의 JobId 업데이트
            TextbookThumbnail thumbnail = existingThumbnail.get();
            // 새로운 작업을 위해 기존 정보를 초기화하고 새 JobId 설정
            TextbookThumbnail newThumbnail = TextbookThumbnail.builder()
                .textbook(textbook)
                .jobId(jobId)
                .build();

            // 기존 썸네일 삭제 후 새로 생성
            thumbnailRepository.delete(thumbnail);
            thumbnailRepository.save(newThumbnail);
            log.info("기존 썸네일 교체 완료");
        } else {
            // 새 썸네일 정보 생성
            TextbookThumbnail newThumbnail = TextbookThumbnail.builder()
                .textbook(textbook)
                .jobId(jobId)
                .build();
            thumbnailRepository.save(newThumbnail);
            log.info("새 썸네일 작업 생성 완료");
        }

        return jobId;
    }

    @Transactional(readOnly = true)
    public Optional<TextbookThumbnailResponseDto> getThumbnailByTextbookId(Long textbookId) {
        log.info("교재 썸네일 조회: TextbookId={}", textbookId);

        return thumbnailRepository.findByTextbookId(textbookId)
            .map(TextbookThumbnailResponseDto::from);
    }

    @Transactional
    public void updateThumbnailManually(Long textbookId, ThumbnailCallbackRequestDto request) {
        log.info("교재 썸네일 수동 업데이트: TextbookId={}", textbookId);

        // 교재 존재 확인
        Textbook textbook = textbookRepository.findById(textbookId)
            .orElseThrow(() -> new IllegalArgumentException("해당 교재를 찾을 수 없습니다: " + textbookId));

        // 기존 썸네일 정보 조회
        Optional<TextbookThumbnail> existingThumbnail = thumbnailRepository.findByTextbookId(textbookId);

        if (existingThumbnail.isPresent()) {
            // 기존 썸네일 정보 업데이트
            TextbookThumbnail thumbnail = existingThumbnail.get();
            thumbnail.updateThumbnailInfo(
                request.getPdfName(),
                request.getThumbnailUrl(),
                request.getS3Key(),
                request.getWidth(),
                request.getHeight()
            );
            thumbnailRepository.save(thumbnail);
        } else {
            // 새 썸네일 정보 생성
            TextbookThumbnail newThumbnail = TextbookThumbnail.builder()
                .textbook(textbook)
                .jobId(request.getJobId())
                .pdfName(request.getPdfName())
                .thumbnailUrl(request.getThumbnailUrl())
                .s3Key(request.getS3Key())
                .width(request.getWidth())
                .height(request.getHeight())
                .build();
            thumbnailRepository.save(newThumbnail);
        }

        log.info("교재 썸네일 수동 업데이트 완료");
    }
}
