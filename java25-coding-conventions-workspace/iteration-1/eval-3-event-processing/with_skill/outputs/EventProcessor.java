package events;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public final class EventProcessor {

    public String process(final Event event) {
        return switch (event) {
            case UserCreated e -> summarizeUserCreated(e);
            case OrderPlaced e -> summarizeOrderPlaced(e);
            case PaymentProcessed e -> summarizePaymentProcessed(e);
        };
    }

    public Map<String, List<Event>> groupByType(final List<Event> events) {
        return events.stream()
                .collect(Collectors.groupingBy(
                        this::typeName,
                        Collectors.toUnmodifiableList()));
    }

    private String typeName(final Event event) {
        return switch (event) {
            case UserCreated _ -> "UserCreated";
            case OrderPlaced _ -> "OrderPlaced";
            case PaymentProcessed _ -> "PaymentProcessed";
        };
    }

    private static String summarizeUserCreated(final UserCreated event) {
        return "User created: " + event.userId() + " (" + event.email() + ")";
    }

    private static String summarizeOrderPlaced(final OrderPlaced event) {
        final var itemCount = event.items().size();
        return "Order placed: " + event.orderId()
                + " by user " + event.userId()
                + " with " + itemCount + " item(s)";
    }

    private static String summarizePaymentProcessed(final PaymentProcessed event) {
        final var status = event.successful() ? "successful" : "failed";
        return "Payment " + event.paymentId()
                + ": " + status
                + " for $" + event.amount();
    }
}
