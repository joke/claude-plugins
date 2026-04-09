package com.example.service;

import java.util.List;
import java.util.Optional;

public class UserService {

    private final UserRepository userRepository;

    public UserService(final UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public String getDisplayName(final String userId) {
        final User user = userRepository.findById(userId);
        if (user == null) {
            return "Unknown";
        }
        // nickname might be null
        if (user.getNickname() != null) {
            return user.getNickname();
        }
        return user.getFullName();
    }

    @SuppressWarnings("NullAway")
    public String getEmail(final String userId) {
        return userRepository.findById(userId).getEmail();
    }

    public List<String> getActiveEmails(final List<String> userIds) {
        final List<String> emails = new java.util.ArrayList<>();
        for (final String id : userIds) {
            final User user = userRepository.findById(id);
            if (user != null && user.getEmail() != null) {
                emails.add(user.getEmail());
            }
        }
        return emails;
    }
}
