package com.example.api;

import java.util.List;
import java.util.stream.Collectors;

public record ApiResponse(int statusCode, String message, Object data, List<String> errors) {

    public ApiResponse(int statusCode, String message, Object data, List<String> errors) {
        this.statusCode = statusCode;
        this.message = message;
        this.data = data;
        this.errors = errors != null ? List.copyOf(errors) : List.of();
    }

    public boolean isSuccessful() {
        return statusCode >= 200 && statusCode < 300;
    }

    public boolean hasErrors() {
        return !errors.isEmpty();
    }

    public String toJson() {
        var errorsJson = errors.stream()
                .map(e -> "    \"%s\"".formatted(e))
                .collect(Collectors.joining(",\n"));

        return """
                {
                  "statusCode": %d,
                  "message": "%s",
                  "successful": %s,\
                %s\
                %s
                }""".formatted(
                statusCode,
                message,
                isSuccessful(),
                data != null ? "\n  \"data\": \"%s\",".formatted(data.toString()) : "",
                !errors.isEmpty() ? """

                  "errors": [
                %s
                  ]""".formatted(errorsJson) : "");
    }

    public static ApiResponse success(String message, Object data) {
        return new ApiResponse(200, message, data, null);
    }

    public static ApiResponse error(int statusCode, String message, List<String> errors) {
        return new ApiResponse(statusCode, message, null, errors);
    }

    public String getStatusCategory() {
        return switch (statusCode / 100) {
            case 2 -> "SUCCESS";
            case 4 -> "CLIENT_ERROR";
            case 5 -> "SERVER_ERROR";
            default -> "OTHER";
        };
    }
}
