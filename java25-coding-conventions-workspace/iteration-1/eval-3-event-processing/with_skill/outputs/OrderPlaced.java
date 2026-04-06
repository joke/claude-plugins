package events;

import java.util.List;
import java.util.Objects;

public record OrderPlaced(String orderId, String userId, List<String> items) implements Event {

    public OrderPlaced {
        Objects.requireNonNull(orderId, "orderId must not be null");
        Objects.requireNonNull(userId, "userId must not be null");
        items = List.copyOf(items);
    }
}
