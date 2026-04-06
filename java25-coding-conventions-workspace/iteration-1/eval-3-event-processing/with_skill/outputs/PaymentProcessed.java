package events;

import java.util.Objects;

public record PaymentProcessed(String paymentId, double amount, boolean successful) implements Event {

    public PaymentProcessed {
        Objects.requireNonNull(paymentId, "paymentId must not be null");
    }
}
