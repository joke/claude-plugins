package com.example.service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class PaymentProcessor {

    private final PaymentGateway gateway;
    private final AuditLogger auditLogger;
    private final double feePercentage;

    public PaymentProcessor(final PaymentGateway gateway, final AuditLogger auditLogger, final double feePercentage) {
        this.gateway = gateway;
        this.auditLogger = auditLogger;
        this.feePercentage = feePercentage;
    }

    public PaymentResult processPayment(final String customerId, final double amount, final String currency) {
        validateCustomerId(customerId);
        validateAmount(amount);

        final double totalAmount = calculateTotalWithFee(amount);
        final PaymentResult result = gateway.charge(customerId, totalAmount, currency);

        logPaymentOutcome(customerId, totalAmount, currency, result);

        return result;
    }

    public PaymentSummary generateMonthlySummary(final String customerId, final List<Payment> payments) {
        final List<Payment> customerPayments = filterByCustomer(customerId, payments);

        final double totalCharged = sumAmounts(customerPayments);
        final double totalFees = sumFees(customerPayments);
        final int successfulCount = countSuccessful(customerPayments);
        final int failedCount = countFailed(customerPayments);
        final List<String> failureReasons = collectFailureReasons(customerPayments);

        return new PaymentSummary(customerId, totalCharged, totalFees, successfulCount, failedCount, failureReasons);
    }

    private static void validateCustomerId(final String customerId) {
        if (customerId == null || customerId.isEmpty()) {
            throw new IllegalArgumentException("Invalid customer ID");
        }
    }

    private static void validateAmount(final double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
    }

    private double calculateTotalWithFee(final double amount) {
        final double fee = amount * feePercentage / 100.0;
        return amount + fee;
    }

    private void logPaymentOutcome(final String customerId, final double totalAmount, final String currency, final PaymentResult result) {
        if (result.isSuccessful()) {
            auditLogger.log("Payment successful for customer " + customerId + ": " + totalAmount + " " + currency);
        } else {
            auditLogger.log("Payment failed for customer " + customerId + ": " + result.getErrorMessage());
        }
    }

    private static List<Payment> filterByCustomer(final String customerId, final List<Payment> payments) {
        final List<Payment> filtered = new ArrayList<>();
        for (final Payment payment : payments) {
            if (payment.getCustomerId().equals(customerId)) {
                filtered.add(payment);
            }
        }
        return Collections.unmodifiableList(filtered);
    }

    private static double sumAmounts(final List<Payment> payments) {
        double total = 0;
        for (final Payment payment : payments) {
            if (payment.isSuccessful()) {
                total += payment.getAmount();
            }
        }
        return total;
    }

    private static double sumFees(final List<Payment> payments) {
        double total = 0;
        for (final Payment payment : payments) {
            if (payment.isSuccessful()) {
                total += payment.getFee();
            }
        }
        return total;
    }

    private static int countSuccessful(final List<Payment> payments) {
        int count = 0;
        for (final Payment payment : payments) {
            if (payment.isSuccessful()) {
                count++;
            }
        }
        return count;
    }

    private static int countFailed(final List<Payment> payments) {
        int count = 0;
        for (final Payment payment : payments) {
            if (!payment.isSuccessful()) {
                count++;
            }
        }
        return count;
    }

    private static List<String> collectFailureReasons(final List<Payment> payments) {
        final List<String> reasons = new ArrayList<>();
        for (final Payment payment : payments) {
            if (!payment.isSuccessful()) {
                reasons.add(payment.getErrorMessage());
            }
        }
        return Collections.unmodifiableList(reasons);
    }
}
