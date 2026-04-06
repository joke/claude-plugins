package com.example.api;

import java.util.Collections;
import java.util.List;

public class ApiResponse {

    private final int statusCode;
    private final String message;
    private final Object data;
    private final List<String> errors;

    public ApiResponse(int statusCode, String message, Object data, List<String> errors) {
        this.statusCode = statusCode;
        this.message = message;
        this.data = data;
        this.errors = errors != null ? Collections.unmodifiableList(new java.util.ArrayList<>(errors)) : Collections.emptyList();
    }

    public int getStatusCode() {
        return statusCode;
    }

    public String getMessage() {
        return message;
    }

    public Object getData() {
        return data;
    }

    public List<String> getErrors() {
        return errors;
    }

    public boolean isSuccessful() {
        return statusCode >= 200 && statusCode < 300;
    }

    public boolean hasErrors() {
        return !errors.isEmpty();
    }

    public String toJson() {
        String json = "{\n";
        json += "  \"statusCode\": " + statusCode + ",\n";
        json += "  \"message\": \"" + message + "\",\n";
        json += "  \"successful\": " + isSuccessful() + ",\n";
        if (data != null) {
            json += "  \"data\": \"" + data.toString() + "\",\n";
        }
        if (!errors.isEmpty()) {
            json += "  \"errors\": [\n";
            for (int i = 0; i < errors.size(); i++) {
                json += "    \"" + errors.get(i) + "\"";
                if (i < errors.size() - 1) {
                    json += ",";
                }
                json += "\n";
            }
            json += "  ]\n";
        }
        json += "}";
        return json;
    }

    public static ApiResponse success(String message, Object data) {
        return new ApiResponse(200, message, data, null);
    }

    public static ApiResponse error(int statusCode, String message, List<String> errors) {
        return new ApiResponse(statusCode, message, null, errors);
    }

    public String getStatusCategory() {
        if (statusCode >= 200 && statusCode < 300) {
            return "SUCCESS";
        } else if (statusCode >= 400 && statusCode < 500) {
            return "CLIENT_ERROR";
        } else if (statusCode >= 500) {
            return "SERVER_ERROR";
        } else {
            return "OTHER";
        }
    }
}
