package com.dyslexia.dyslexia.controller;

import com.dyslexia.dyslexia.dto.CommonResponse;
import com.dyslexia.dyslexia.dto.ThumbnailCallbackRequestDto;
import com.dyslexia.dyslexia.dto.TextbookThumbnailResponseDto;
import com.dyslexia.dyslexia.service.TextbookThumbnailService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/textbook")
@Tag(name = "교재 썸네일", description = "교재 썸네일 관리 API")
public class TextbookThumbnailController {

    private final TextbookThumbnailService thumbnailService;

    @Value("${external.callback.token:}")
    private String expectedCallbackToken;

    @Operation(
        summary = "썸네일 생성 완료 콜백",
        description = """
            FastAPI에서 썸네일 생성 완료 시 호출하는 콜백 엔드포인트입니다.
            X-Callback-Token 헤더로 인증을 수행합니다.
            """
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "콜백 처리 성공",
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = CommonResponse.class)
            )
        ),
        @ApiResponse(responseCode = "400", description = "잘못된 요청"),
        @ApiResponse(responseCode = "401", description = "인증 실패"),
        @ApiResponse(responseCode = "404", description = "작업 ID를 찾을 수 없음")
    })
    @PostMapping(
        path = "/thumbnail/{jobId}",
        consumes = MediaType.APPLICATION_JSON_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<?> handleThumbnailCallback(
        @Parameter(description = "작업 ID", required = true)
        @PathVariable String jobId,

        @Parameter(description = "썸네일 콜백 데이터", required = true)
        @Valid @RequestBody ThumbnailCallbackRequestDto request,

        @Parameter(description = "콜백 인증 토큰", required = false)
        @RequestHeader(value = "X-Callback-Token", required = false) String callbackToken,

        HttpServletRequest httpRequest) {

        log.info("=== 썸네일 콜백 요청 수신 ===");
        log.info("JobId: {}, ThumbnailUrl: {}, ClientIP: {}",
                jobId, request.getThumbnailUrl(), httpRequest.getRemoteAddr());

        // 콜백 토큰 검증 (설정된 경우에만)
        if (!expectedCallbackToken.isEmpty()) {
            if (callbackToken == null || !expectedCallbackToken.equals(callbackToken)) {
                log.warn("콜백 토큰 인증 실패: Expected={}, Received={}",
                        expectedCallbackToken, callbackToken);
                return ResponseEntity.status(401)
                    .body(new CommonResponse<>("인증 실패", null));
            }
        }

        try {
            thumbnailService.handleThumbnailCallback(jobId, request);

            log.info("썸네일 콜백 처리 완료: JobId={}", jobId);
            return ResponseEntity.ok(new CommonResponse<>("썸네일 생성 완료", null));

        } catch (IllegalArgumentException e) {
            log.error("썸네일 콜백 처리 실패: {}", e.getMessage());
            return ResponseEntity.badRequest()
                .body(new CommonResponse<>("처리 실패: " + e.getMessage(), null));

        } catch (Exception e) {
            log.error("썸네일 콜백 처리 중 오류 발생", e);
            return ResponseEntity.internalServerError()
                .body(new CommonResponse<>("서버 오류가 발생했습니다", null));
        }
    }

    @Operation(
        summary = "교재 썸네일 조회",
        description = "교재 ID로 썸네일 정보를 조회합니다."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "조회 성공",
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = TextbookThumbnailResponseDto.class)
            )
        ),
        @ApiResponse(responseCode = "404", description = "썸네일 정보를 찾을 수 없음")
    })
    @GetMapping("/v1/textbooks/{textbookId}/thumbnail")
    public ResponseEntity<?> getThumbnail(
        @Parameter(description = "교재 ID", required = true)
        @PathVariable Long textbookId) {

        log.info("교재 썸네일 조회 요청: TextbookId={}", textbookId);

        try {
            Optional<TextbookThumbnailResponseDto> thumbnail = thumbnailService.getThumbnailByTextbookId(textbookId);

            if (thumbnail.isPresent()) {
                return ResponseEntity.ok(new CommonResponse<>("썸네일 조회 성공", thumbnail.get()));
            } else {
                return ResponseEntity.status(404)
                    .body(new CommonResponse<>("해당 교재의 썸네일 정보가 없습니다", null));
            }

        } catch (Exception e) {
            log.error("썸네일 조회 중 오류 발생", e);
            return ResponseEntity.internalServerError()
                .body(new CommonResponse<>("서버 오류가 발생했습니다", null));
        }
    }

    @Operation(
        summary = "교재 썸네일 수동 업데이트",
        description = "교재의 썸네일 정보를 수동으로 업데이트합니다."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "업데이트 성공"),
        @ApiResponse(responseCode = "400", description = "잘못된 요청"),
        @ApiResponse(responseCode = "404", description = "교재를 찾을 수 없음")
    })
    @PutMapping(
        path = "/v1/textbooks/{textbookId}/thumbnail",
        consumes = MediaType.APPLICATION_JSON_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<?> updateThumbnail(
        @Parameter(description = "교재 ID", required = true)
        @PathVariable Long textbookId,

        @Parameter(description = "썸네일 정보", required = true)
        @Valid @RequestBody ThumbnailCallbackRequestDto request) {

        log.info("교재 썸네일 수동 업데이트 요청: TextbookId={}", textbookId);

        try {
            thumbnailService.updateThumbnailManually(textbookId, request);

            return ResponseEntity.ok(new CommonResponse<>("썸네일 업데이트 완료", null));

        } catch (IllegalArgumentException e) {
            log.error("썸네일 업데이트 실패: {}", e.getMessage());
            return ResponseEntity.badRequest()
                .body(new CommonResponse<>("업데이트 실패: " + e.getMessage(), null));

        } catch (Exception e) {
            log.error("썸네일 업데이트 중 오류 발생", e);
            return ResponseEntity.internalServerError()
                .body(new CommonResponse<>("서버 오류가 발생했습니다", null));
        }
    }
}
