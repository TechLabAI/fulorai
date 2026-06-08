package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.ConversaCopilotoEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.UUID;

@Repository
public interface ConversaCopilotoRepository extends JpaRepository<ConversaCopilotoEntity, UUID> {

}
