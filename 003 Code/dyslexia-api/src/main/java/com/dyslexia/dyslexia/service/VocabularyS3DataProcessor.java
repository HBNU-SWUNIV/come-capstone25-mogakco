package com.dyslexia.dyslexia.service;

import com.dyslexia.dyslexia.domain.pdf.VocabularyAnalysis;
import com.dyslexia.dyslexia.dto.VocabularyItemDto;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class VocabularyS3DataProcessor {

    private final ObjectMapper objectMapper;

    public List<VocabularyAnalysis> processS3SummaryData(JsonNode summaryData, Long textbookId) {
        if (summaryData == null) {
            log.warn("S3 summary 데이터가 null입니다");
            return new ArrayList<>();
        }

        List<VocabularyAnalysis> entities = new ArrayList<>();

        try {
            // summary 구조 분석 및 처리
            if (summaryData.isArray()) {
                for (JsonNode blockNode : summaryData) {
                    entities.addAll(processBlockNode(blockNode, textbookId));
                }
            } else if (summaryData.has("blocks")) {
                JsonNode blocksNode = summaryData.get("blocks");
                if (blocksNode.isArray()) {
                    for (JsonNode blockNode : blocksNode) {
                        entities.addAll(processBlockNode(blockNode, textbookId));
                    }
                }
            } else {
                // 단일 블록 처리
                entities.addAll(processBlockNode(summaryData, textbookId));
            }

            log.info("S3 summary 데이터 처리 완료: {} 개 항목 생성", entities.size());

        } catch (Exception e) {
            log.error("S3 summary 데이터 처리 중 오류 발생", e);
        }

        return entities;
    }

    private List<VocabularyAnalysis> processBlockNode(JsonNode blockNode, Long textbookId) {
        List<VocabularyAnalysis> entities = new ArrayList<>();

        try {
            String blockId = getTextValue(blockNode, "block_id", "blockId");
            Integer pageNumber = getIntValue(blockNode, "page_number", "pageNumber");
            String createdAtStr = getTextValue(blockNode, "created_at", "createdAt");

            // vocabulary_items 또는 vocabularyItems 필드에서 어휘 항목들 추출
            JsonNode itemsNode = blockNode.has("vocabulary_items")
                ? blockNode.get("vocabulary_items")
                : blockNode.get("vocabularyItems");

            if (itemsNode != null && itemsNode.isArray()) {
                for (JsonNode itemNode : itemsNode) {
                    VocabularyItemDto item = parseVocabularyItem(itemNode);
                    if (item != null) {
                        VocabularyAnalysis entity = toEntity(textbookId, pageNumber, blockId, item, createdAtStr);
                        entities.add(entity);
                    }
                }
            }

            log.debug("블록 처리 완료: blockId={}, pageNumber={}, items={}", blockId, pageNumber, entities.size());

        } catch (Exception e) {
            log.error("블록 노드 처리 중 오류 발생", e);
        }

        return entities;
    }

    private VocabularyItemDto parseVocabularyItem(JsonNode itemNode) {
        try {
            VocabularyItemDto item = new VocabularyItemDto();

            item.setWord(getTextValue(itemNode, "word"));
            item.setStartIndex(getIntValue(itemNode, "start_index", "startIndex"));
            item.setEndIndex(getIntValue(itemNode, "end_index", "endIndex"));
            item.setDefinition(getTextValue(itemNode, "definition"));
            item.setSimplifiedDefinition(getTextValue(itemNode, "simplified_definition", "simplifiedDefinition"));
            item.setDifficultyLevel(getTextValue(itemNode, "difficulty_level", "difficultyLevel"));
            item.setReason(getTextValue(itemNode, "reason"));
            item.setGradeLevel(getIntValue(itemNode, "grade_level", "gradeLevel"));

            // examples 처리
            JsonNode examplesNode = itemNode.has("examples") ? itemNode.get("examples") : null;
            if (examplesNode != null) {
                if (examplesNode.isTextual()) {
                    item.setExamples(examplesNode.textValue());
                } else {
                    item.setExamples(objectMapper.writeValueAsString(examplesNode));
                }
            }

            // phoneme_analysis 처리
            JsonNode phonemeNode = itemNode.has("phoneme_analysis") ? itemNode.get("phoneme_analysis") : null;
            if (phonemeNode != null) {
                if (phonemeNode.isTextual()) {
                    item.setPhonemeAnalysisJson(phonemeNode.textValue());
                } else {
                    item.setPhonemeAnalysis(objectMapper.convertValue(phonemeNode, Object.class));
                }
            }

            return item;

        } catch (Exception e) {
            log.error("어휘 항목 파싱 중 오류 발생", e);
            return null;
        }
    }

    private VocabularyAnalysis toEntity(Long textbookId, Integer pageNumber, String blockId,
                                      VocabularyItemDto item, String createdAtStr) {

        String examplesText = null;
        try {
            if (item.getExamples() != null) {
                if (item.getExamples() instanceof String) {
                    examplesText = (String) item.getExamples();
                } else {
                    examplesText = objectMapper.writeValueAsString(item.getExamples());
                }
            }
        } catch (Exception e) {
            log.warn("examples 직렬화 실패 - 문자열로 저장하지 않음. blockId={}, word={}", blockId, item.getWord());
        }

        String phonemeJson = null;
        try {
            if (item.getPhonemeAnalysisJson() != null && !item.getPhonemeAnalysisJson().isBlank()) {
                phonemeJson = item.getPhonemeAnalysisJson();
            } else if (item.getPhonemeAnalysis() != null) {
                phonemeJson = objectMapper.writeValueAsString(item.getPhonemeAnalysis());
            }
        } catch (Exception e) {
            log.warn("phonemeAnalysis 직렬화 실패 - 생략. blockId={}, word={}, error={}", blockId, item.getWord(), e.getMessage());
        }

        LocalDateTime createdAt = parseDateTime(createdAtStr);

        return VocabularyAnalysis.builder()
            .textbookId(textbookId)
            .pageNumber(pageNumber)
            .blockId(blockId)
            .word(item.getWord())
            .startIndex(item.getStartIndex())
            .endIndex(item.getEndIndex())
            .definition(trim255(item.getDefinition()))
            .simplifiedDefinition(trim255(item.getSimplifiedDefinition()))
            .examples(examplesText)
            .difficultyLevel(item.getDifficultyLevel())
            .reason(trim255(item.getReason()))
            .gradeLevel(item.getGradeLevel())
            .phonemeAnalysisJson(phonemeJson)
            .createdAt(createdAt != null ? createdAt : LocalDateTime.now())
            .build();
    }

    private String getTextValue(JsonNode node, String... fieldNames) {
        for (String fieldName : fieldNames) {
            JsonNode field = node.get(fieldName);
            if (field != null && !field.isNull()) {
                return field.isTextual() ? field.textValue() : field.toString();
            }
        }
        return null;
    }

    private Integer getIntValue(JsonNode node, String... fieldNames) {
        for (String fieldName : fieldNames) {
            JsonNode field = node.get(fieldName);
            if (field != null && !field.isNull() && field.isNumber()) {
                return field.intValue();
            }
        }
        return null;
    }

    private static String trim255(String s) {
        if (s == null) return null;
        return s.length() <= 255 ? s : s.substring(0, 255);
    }

    private static LocalDateTime parseDateTime(String iso) {
        if (iso == null || iso.isBlank()) return null;
        try {
            return OffsetDateTime.parse(iso).toLocalDateTime();
        } catch (DateTimeParseException e) {
            try {
                return LocalDateTime.parse(iso);
            } catch (DateTimeParseException ignored) {
                return null;
            }
        }
    }
}