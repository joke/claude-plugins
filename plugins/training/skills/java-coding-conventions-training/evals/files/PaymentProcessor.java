package com.example.service;

import java.util.ArrayList;
import java.util.List;

public class PaymentProcessor {

    private PaymentGateway gateway;
    private AuditLogger auditLogger;
    private double feePercentage;

    public PaymentProcessor() {
    }

    public void setGateway(PaymentGateway gateway) {
        this.gateway = gateway;
    }

    public void setAuditLogger(AuditLogger auditLogger) {
        this.auditLogger = auditLogger;
    }

    public void setFeePercentage(double feePercentage) {
        this.feePercentage = feePercentage;
    }

    public PaymentResult processPayment(String customerId, double amount, String currency) throws PaymentException {
        if (customerId == null || customerId.isEmpty()) {
            throw new PaymentException("Invalid customer ID");
        }
        if (amount <= 0) {
            throw new PaymentException("Amount must be positive");
        }

        double fee = amount * feePercentage / 100.0;
        double totalAmount = amount + fee;

        PaymentResult result = gateway.charge(customerId, totalAmount, currency);

        if (result.isSuccessful()) {
            auditLogger.log("Payment successful for customer " + customerId + ": " + totalAmount + " " + currency);
        } else {
            auditLogger.log("Payment failed for customer " + customerId + ": " + result.getErrorMessage());
        }

        return result;
    }

    public PaymentSummary generateMonthlySummary(String customerId, List<Payment> payments) throws Exception {
        double totalCharged = 0;
        double totalFees = 0;
        int successfulCount = 0;
        int failedCount = 0;
        List<String> failureReasons = new ArrayList<>();

        for (Payment payment : payments) {
            if (payment.getCustomerId().equals(customerId)) {
                if (payment.isSuccessful()) {
                    successfulCount++;
                    totalCharged += payment.getAmount();
                    totalFees += payment.getFee();
                } else {
                    failedCount++;
                    failureReasons.add(payment.getErrorMessage());
                }
            }
        }

        PaymentSummary summary = new PaymentSummary();
        summary.setCustomerId(customerId);
        summary.setTotalCharged(totalCharged);
        summary.setTotalFees(totalFees);
        summary.setSuccessfulCount(successfulCount);
        summary.setFailedCount(failedCount);
        summary.setFailureReasons(failureReasons);

        return summary;
    }
}
