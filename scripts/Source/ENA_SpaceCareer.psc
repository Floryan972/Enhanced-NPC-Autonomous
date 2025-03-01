Scriptname ENA_SpaceCareer extends Quest
{Handles NPC career progression and job assignments in space}

; Import required game systems
import Game
import Debug
import Utility
import Actor

; Enums and Structs
Struct Career
    String path ; COMMAND, ENGINEERING, SCIENCE, TRADE
    int level
    float experience
    String[] achievements
    Form[] certifications
EndStruct

Struct JobAssignment
    String title
    Location workplace
    float salary
    String[] responsibilities
    ActorBase[] colleagues
    bool isTemporary
EndStruct

Struct SkillProgression
    String skillName
    float level
    float experience
    String[] specializations
    bool isSpaceRelated
EndStruct

; Properties
Career[] Property ActiveCareers Auto
JobAssignment[] Property CurrentAssignments Auto
float Property UpdateInterval = 24.0 Auto

; Events
Event OnInit()
    Initialize()
    RegisterForUpdateGameTime(UpdateInterval)
EndEvent

Event OnUpdateGameTime()
    UpdateCareers()
EndEvent

; Core functions
Function Initialize()
    InitializeCareers()
    SetupInitialJobs()
EndFunction

Function InitializeCareers()
    Actor[] npcs = Game.GetAllActors()
    
    int i = 0
    while i < npcs.Length
        Actor npc = npcs[i]
        if IsSpaceCareerNPC(npc)
            Career career = CreateCareer(npc)
            AssignCareer(npc, career)
        endif
        i += 1
    endwhile
EndFunction

; Career management
Career Function CreateCareer(Actor npc)
    Career career = new Career
    
    ; Determine career path based on skills
    if HasCommandSkills(npc)
        SetupCommandCareer(career)
    elseif HasEngineeringSkills(npc)
        SetupEngineeringCareer(career)
    elseif HasScienceSkills(npc)
        SetupScienceCareer(career)
    elseif HasTradeSkills(npc)
        SetupTradeCareer(career)
    endif
    
    return career
EndFunction

Function UpdateCareer(Actor npc)
    Career career = GetNPCCareer(npc)
    if career
        ; Update experience
        career.experience += CalculateExperienceGain(npc)
        
        ; Check for level up
        if CanLevelUp(career)
            LevelUpCareer(npc, career)
        endif
        
        ; Update achievements
        CheckForAchievements(npc, career)
        
        ; Update certifications
        UpdateCertifications(npc, career)
    endif
EndFunction

Function LevelUpCareer(Actor npc, Career career)
    career.level += 1
    
    ; Update benefits
    UpdateSalary(npc)
    UpdatePrivileges(npc)
    
    ; New responsibilities
    AssignNewResponsibilities(npc)
    
    ; Notification
    Debug.Notification(npc.GetDisplayName() + " has been promoted to level " + career.level)
EndFunction

; Job management
Function SetupInitialJobs()
    Actor[] npcs = Game.GetAllActors()
    
    int i = 0
    while i < npcs.Length
        Actor npc = npcs[i]
        if IsSpaceCareerNPC(npc)
            JobAssignment job = CreateInitialJob(npc)
            AssignJob(npc, job)
        endif
        i += 1
    endwhile
EndFunction

JobAssignment Function CreateInitialJob(Actor npc)
    JobAssignment job = new JobAssignment
    Career career = GetNPCCareer(npc)
    
    if career
        if career.path == "COMMAND"
            SetupCommandJob(job)
        elseif career.path == "ENGINEERING"
            SetupEngineeringJob(job)
        elseif career.path == "SCIENCE"
            SetupScienceJob(job)
        elseif career.path == "TRADE"
            SetupTradeJob(job)
        endif
    endif
    
    return job
EndFunction

Function UpdateJob(Actor npc)
    JobAssignment job = GetNPCJob(npc)
    if job
        ; Update performance
        float performance = EvaluateJobPerformance(npc)
        
        ; Handle promotion/demotion
        if performance > 0.8
            ConsiderPromotion(npc)
        elseif performance < 0.3
            ConsiderDemotion(npc)
        endif
        
        ; Update responsibilities
        UpdateJobResponsibilities(npc, job)
    endif
EndFunction

; Skill progression
Function UpdateSkills(Actor npc)
    SkillProgression[] skills = GetNPCSkills(npc)
    
    int i = 0
    while i < skills.Length
        SkillProgression skill = skills[i]
        
        ; Update skill experience
        skill.experience += CalculateSkillExperience(npc, skill)
        
        ; Check for skill level up
        if CanSkillLevelUp(skill)
            LevelUpSkill(npc, skill)
        endif
        
        ; Update specializations
        UpdateSkillSpecializations(skill)
        
        i += 1
    endwhile
EndFunction

Function LevelUpSkill(Actor npc, SkillProgression skill)
    skill.level += 1
    
    ; Update related abilities
    UpdateNPCAbilities(npc, skill)
    
    ; Unlock new specializations
    UnlockNewSpecializations(skill)
    
    ; Career implications
    CheckCareerAdvancement(npc, skill)
EndFunction

; Performance evaluation
float Function EvaluateJobPerformance(Actor npc)
    float performance = 0.5 ; Base performance
    
    ; Task completion
    performance += GetTaskCompletionRate(npc) * 0.3
    
    ; Skill utilization
    performance += GetSkillUtilization(npc) * 0.2
    
    ; Colleague feedback
    performance += GetColleagueFeedback(npc) * 0.2
    
    ; Attendance
    performance += GetAttendanceRate(npc) * 0.1
    
    return Math.Clamp(performance, 0.0, 1.0)
EndFunction

Function HandlePerformanceReview(Actor npc)
    float performance = EvaluateJobPerformance(npc)
    
    ; Handle results
    if performance >= 0.9
        GiveExceptionalReview(npc)
    elseif performance >= 0.7
        GivePositiveReview(npc)
    elseif performance >= 0.4
        GiveAverageReview(npc)
    else
        GiveNegativeReview(npc)
    endif
EndFunction

; Utility functions
bool Function IsSpaceCareerNPC(Actor npc)
    return npc && !npc.IsDead() && npc.HasKeyword(Game.GetForm("SpaceCareerKeyword") as Keyword)
EndFunction

Function UpdateCareers()
    Actor[] npcs = Game.GetAllActors()
    
    int i = 0
    while i < npcs.Length
        Actor npc = npcs[i]
        if IsSpaceCareerNPC(npc)
            ; Update career progression
            UpdateCareer(npc)
            
            ; Update current job
            UpdateJob(npc)
            
            ; Update skills
            UpdateSkills(npc)
            
            ; Periodic performance review
            if ShouldDoPerformanceReview(npc)
                HandlePerformanceReview(npc)
            endif
        endif
        i += 1
    endwhile
EndFunction
