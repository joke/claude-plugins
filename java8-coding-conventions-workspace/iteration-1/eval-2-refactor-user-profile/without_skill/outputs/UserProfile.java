package com.example.model;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

public final class UserProfile {

    private final String id;
    private final String name;
    private final String email;
    private final List<String> roles;
    private final boolean active;

    private UserProfile(Builder builder) {
        this.id = Objects.requireNonNull(builder.id, "id must not be null");
        this.name = Objects.requireNonNull(builder.name, "name must not be null");
        this.email = Objects.requireNonNull(builder.email, "email must not be null");
        this.roles = Collections.unmodifiableList(new ArrayList<>(
                Optional.ofNullable(builder.roles).orElseGet(Collections::emptyList)));
        this.active = builder.active;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public List<String> getRoles() {
        return roles;
    }

    public boolean isActive() {
        return active;
    }

    public boolean hasRole(String role) {
        return roles.stream().anyMatch(r -> r.equals(role));
    }

    public List<String> getActiveRoles() {
        return roles.stream()
                .filter(role -> !"INACTIVE".equals(role))
                .collect(Collectors.toList());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof UserProfile)) return false;
        UserProfile that = (UserProfile) o;
        return active == that.active
                && Objects.equals(id, that.id)
                && Objects.equals(name, that.name)
                && Objects.equals(email, that.email)
                && Objects.equals(roles, that.roles);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, email, roles, active);
    }

    @Override
    public String toString() {
        return "UserProfile{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", email='" + email + '\'' +
                ", roles=" + roles +
                ", active=" + active +
                '}';
    }

    public static Builder builder() {
        return new Builder();
    }

    public static final class Builder {

        private String id;
        private String name;
        private String email;
        private List<String> roles = new ArrayList<>();
        private boolean active;

        private Builder() {
        }

        public Builder id(String id) {
            this.id = id;
            return this;
        }

        public Builder name(String name) {
            this.name = name;
            return this;
        }

        public Builder email(String email) {
            this.email = email;
            return this;
        }

        public Builder roles(List<String> roles) {
            this.roles = roles;
            return this;
        }

        public Builder active(boolean active) {
            this.active = active;
            return this;
        }

        public UserProfile build() {
            return new UserProfile(this);
        }
    }
}
