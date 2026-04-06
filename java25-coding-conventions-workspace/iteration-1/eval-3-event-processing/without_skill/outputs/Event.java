package event;

import java.util.List;

public sealed interface Event {

    record UserCreated(String userId, String email) implements Event {}

    record OrderPlaced(String orderId, String userId, List<String> items) implements Event {}

    record PaymentProcessed(String paymentId, double amount, boolean successful) implements Event {}
}
