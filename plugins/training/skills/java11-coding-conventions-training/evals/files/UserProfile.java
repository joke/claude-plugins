package com.example.model;

import java.util.ArrayList;
import java.util.List;

public class UserProfile {

    private String id;
    private String name;
    private String email;
    private List<String> roles;
    private boolean active;

    public UserProfile() {
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public List<String> getRoles() {
        return roles;
    }

    public void setRoles(List<String> roles) {
        this.roles = roles;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }

    public boolean hasRole(String role) {
        if (roles == null) {
            return false;
        }
        for (String r : roles) {
            if (r.equals(role)) {
                return true;
            }
        }
        return false;
    }

    public List<String> getActiveRoles() {
        List<String> result = new ArrayList<>();
        if (roles != null) {
            for (String role : roles) {
                if (!role.equals("INACTIVE")) {
                    result.add(role);
                }
            }
        }
        return result;
    }
}
