package com.example.model;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class UserProfile {

    private final String id;
    private final String name;
    private final String email;
    private final List<String> roles;
    private final boolean active;

    public UserProfile(final String id, final String name, final String email,
                       final List<String> roles, final boolean active) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.roles = Collections.unmodifiableList(new ArrayList<>(roles));
        this.active = active;
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

    public boolean hasRole(final String role) {
        return roles.stream()
                .anyMatch(r -> r.equals(role));
    }

    public List<String> getActiveRoles() {
        return roles.stream()
                .filter(role -> !role.equals("INACTIVE"))
                .collect(Collectors.toList());
    }
}
