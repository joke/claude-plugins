package com.example.api;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

public record ApiResponse(int statusCode, String message, Object data, List<String> errors) {

    public ApiResponse {
        Objects.requireNonNull(message, "message must not be null");
        errors = errors != null ? List.copyOf(errors) : List.of();
    }

    public boolean isSuccessful() {
        return statusCode >= 200 && statusCode < 300;
    }

    public boolean hasErrors() {
        return !errors.isEmpty();
    }

    public String toJson() {
        final var builder = new StringBuilder();
        builder.append("""
                {
                  "statusCode": %d,
                  "message": "%s",
                  "successful": %s""".formatted(statusCode, message, isSuccessful()));
        if (data != null) {
            builder.append("""
                    ,
                      "data": "%s\"""".formatted(data.toString()));
        }
        if (!errors.isEmpty()) {
            final var errorEntries = errors.stream()
                    .map(e -> "    \"%s\"".formatted(e))
                    .collect(Collectors.joining(",\n"));
            builder.append("""
                    ,
                      "errors": [
                    %s
                      ]""".formatted(errorEntries));
        }
        builder.append("\n}");
        return builder.toString();
    }

    public String statusCategory() {
        return switch (statusCode / 100) {
            case 2 -> "SUCCESS";
            case 4 -> "CLIENT_ERROR";
            case 5 -> "SERVER_ERROR";
            default -> "OTHER";
        };
    }

    public static ApiResponse success(final String message, final Object data) {
        return new ApiResponse(200, message, data, null);
    }

    public static ApiResponse error(final int statusCode, final String message, final List<String> errors) {
        return new ApiResponse(statusCode, message, null, errors);
    }
}
