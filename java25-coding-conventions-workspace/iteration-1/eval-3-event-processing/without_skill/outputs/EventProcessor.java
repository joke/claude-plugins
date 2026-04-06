package event;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public final class EventProcessor {

    private final List<Event> events;

    public EventProcessor(final List<Event> events) {
        this.events = List.copyOf(events);
    }

    public String process(final Event event) {
        return switch (event) {
            case Event.UserCreated(final var userId, final var email) ->
                formatUserCreated(userId, email);
            case Event.OrderPlaced(final var orderId, final var userId, final var items) ->
                formatOrderPlaced(orderId, userId, items);
            case Event.PaymentProcessed(final var paymentId, final var amount, final var successful) ->
                formatPaymentProcessed(paymentId, amount, successful);
        };
    }

    public List<String> processAll() {
        return events.stream()
            .map(this::process)
            .toList();
    }

    public Map<String, List<Event>> groupByType() {
        return events.stream()
            .collect(Collectors.groupingBy(this::eventTypeName));
    }

    private String eventTypeName(final Event event) {
        return switch (event) {
            case Event.UserCreated _ -> "UserCreated";
            case Event.OrderPlaced _ -> "OrderPlaced";
            case Event.PaymentProcessed _ -> "PaymentProcessed";
        };
    }

    private String formatUserCreated(final String userId, final String email) {
        return "User created: %s (%s)".formatted(userId, email);
    }

    private String formatOrderPlaced(final String orderId, final String userId, final List<String> items) {
        final var itemList = String.join(", ", items);
        return "Order %s placed by %s: [%s]".formatted(orderId, userId, itemList);
    }

    private String formatPaymentProcessed(final String paymentId, final double amount, final boolean successful) {
        final var status = successful ? "successful" : "failed";
        return "Payment %s: $%.2f (%s)".formatted(paymentId, amount, status);
    }
}
