package events;

import java.util.Objects;

public record UserCreated(String userId, String email) implements Event {

    public UserCreated {
        Objects.requireNonNull(userId, "userId must not be null");
        Objects.requireNonNull(email, "email must not be null");
    }
}
