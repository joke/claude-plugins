package com.example.service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class PaymentSummary {

    private final String customerId;
    private final double totalCharged;
    private final double totalFees;
    private final int successfulCount;
    private final int failedCount;
    private final List<String> failureReasons;

    public PaymentSummary(final String customerId,
                          final double totalCharged,
                          final double totalFees,
                          final int successfulCount,
                          final int failedCount,
                          final List<String> failureReasons) {
        this.customerId = customerId;
        this.totalCharged = totalCharged;
        this.totalFees = totalFees;
        this.successfulCount = successfulCount;
        this.failedCount = failedCount;
        this.failureReasons = Collections.unmodifiableList(new ArrayList<>(failureReasons));
    }

    public String getCustomerId() {
        return customerId;
    }

    public double getTotalCharged() {
        return totalCharged;
    }

    public double getTotalFees() {
        return totalFees;
    }

    public int getSuccessfulCount() {
        return successfulCount;
    }

    public int getFailedCount() {
        return failedCount;
    }

    public List<String> getFailureReasons() {
        return failureReasons;
    }
}
