package events;

import java.util.List;
import java.util.Objects;

public sealed interface Event permits UserCreated, OrderPlaced, PaymentProcessed {
}
