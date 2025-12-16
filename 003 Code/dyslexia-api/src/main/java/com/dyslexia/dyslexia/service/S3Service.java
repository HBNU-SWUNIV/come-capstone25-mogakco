package com.dyslexia.dyslexia.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class S3Service {

    private final ObjectMapper objectMapper;
    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(30))
            .build();

    public JsonNode downloadJsonFromS3(String s3Url) {
        if (s3Url == null || s3Url.isBlank()) {
            log.warn("S3 URL이 비어있습니다");
            return null;
        }

        try {
            log.info("S3에서 JSON 다운로드 시작: {}", s3Url);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(s3Url))
                    .timeout(Duration.ofSeconds(60))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request,
                    HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() != 200) {
                log.error("S3 다운로드 실패: status={}, url={}", response.statusCode(), s3Url);
                return null;
            }

            String jsonContent = response.body();
            log.info("S3 JSON 다운로드 완료: size={} bytes", jsonContent.length());

            return objectMapper.readTree(jsonContent);

        } catch (IOException | InterruptedException e) {
            log.error("S3 JSON 다운로드 중 오류 발생: url={}", s3Url, e);
            return null;
        }
    }

    public List<JsonNode> downloadJsonFilesFromS3Prefix(String s3Prefix) {
        if (s3Prefix == null || s3Prefix.isBlank()) {
            log.warn("S3 prefix가 비어있습니다");
            return new ArrayList<>();
        }

        // S3 prefix를 기반으로 파일 목록을 가져와야 하지만,
        // 현재는 실제 AWS SDK 없이 HTTP 클라이언트로 구현
        // 실제 구현에서는 AWS SDK를 사용해야 합니다
        log.warn("S3 prefix 기반 파일 목록 다운로드는 현재 지원되지 않습니다: {}", s3Prefix);
        log.info("단일 파일 다운로드 기능만 현재 지원됩니다");

        return new ArrayList<>();
    }

    public String downloadTextFromS3(String s3Url) {
        if (s3Url == null || s3Url.isBlank()) {
            log.warn("S3 URL이 비어있습니다");
            return null;
        }

        try {
            log.info("S3에서 텍스트 다운로드 시작: {}", s3Url);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(s3Url))
                    .timeout(Duration.ofSeconds(60))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request,
                    HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() != 200) {
                log.error("S3 텍스트 다운로드 실패: status={}, url={}", response.statusCode(), s3Url);
                return null;
            }

            String content = response.body();
            log.info("S3 텍스트 다운로드 완료: size={} bytes", content.length());

            return content;

        } catch (IOException | InterruptedException e) {
            log.error("S3 텍스트 다운로드 중 오류 발생: url={}", s3Url, e);
            return null;
        }
    }
}