from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from database import Base


class SessionStatus:
    planning = "planning"
    fermenting = "fermenting"
    stripping_run = "Stripping Run"
    spirit_run = "Spirit Run"


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    spirit_type = Column(String)            # e.g. "Whisky", "Rum", "Vodka", "Gin"
    mash_bill = Column(Text)               # Free text description of grain bill
    target_wash_og = Column(Float)         # Target original gravity of the wash
    target_wash_abv = Column(Float)        # Target ABV % of the wash
    water_volume_litres = Column(Float)    # Total water volume
    yeast_strain = Column(String)          # e.g. "EC-1118", "US-05"
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    grain_bill = relationship("GrainBill", back_populates="recipe", cascade="all, delete-orphan")
    hops = relationship("HopAddition", back_populates="recipe", cascade="all, delete-orphan")
    yeast = relationship("Yeast", back_populates="recipe", cascade="all, delete-orphan")
    brew_sessions = relationship("BrewSession", back_populates="recipe")
    spirit_runs = relationship("SpiritRun", back_populates="recipe")


class GrainBill(Base):
    __tablename__ = "grain_bill"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    grain_name = Column(String, nullable=False)
    amount_kg = Column(Float, nullable=False)

    recipe = relationship("Recipe", back_populates="grain_bill")


class HopAddition(Base):
    __tablename__ = "hop_additions"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    hop_name = Column(String, nullable=False)
    amount_grams = Column(Float, nullable=False)
    alpha_acid = Column(Float)              # AA%
    addition_time_mins = Column(Integer)    # Minutes from end of boil
    purpose = Column(String)               # "bittering", "flavour", "aroma", "dry hop"

    recipe = relationship("Recipe", back_populates="hops")


class Yeast(Base):
    __tablename__ = "yeast"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    yeast_name = Column(String, nullable=False)
    amount_grams = Column(Float)
    notes = Column(Text)

    recipe = relationship("Recipe", back_populates="yeast")

class SpiritRun(Base):
    __tablename__ = "spirit_runs"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    batch_number = Column(Integer, nullable=False)
    fermentation_start_date = Column(DateTime(timezone=True))
    status = Column(String, default=SessionStatus.planning)


    # Wash
    actual_og = Column(Float)
    actual_fg = Column(Float)
    actual_abv = Column(Float)


    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recipe = relationship("Recipe", back_populates="spirit_runs")
    fermentation_readings = relationship("FermentationReading", back_populates="spirit_session", cascade="all, delete-orphan")

class BrewSession(Base):
    __tablename__ = "brew_sessions"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    batch_number = Column(String)           # e.g. "2024-001"
    brew_date = Column(DateTime(timezone=True))
    status = Column(String, default=SessionStatus.planning)

    # Mash
    mash_temp_c = Column(Float)
    mash_time_mins = Column(Integer)



    # Boil
    boil_time_mins = Column(Integer)
    pre_boil_volume_litres = Column(Float)
    post_boil_volume_litres = Column(Float)

    # Actuals
    actual_og = Column(Float)
    actual_fg = Column(Float)
    actual_abv = Column(Float)
    actual_yield_litres = Column(Float)
    brewhouse_efficiency = Column(Float)    # %

    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipe = relationship("Recipe", back_populates="brew_sessions")
    fermentation_readings = relationship("FermentationReading", back_populates="session", cascade="all, delete-orphan")


class FermentationReading(Base):
    """Stores data from the RAPT Pill hydrometer (and manual entries)."""
    __tablename__ = "fermentation_readings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("brew_sessions.id"), nullable=True)
    spirit_run_id = Column(Integer, ForeignKey("spirit_runs.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    gravity = Column(Float)
    temperature_c = Column(Float)
    battery = Column(Float)                 # RAPT Pill battery %
    rssi = Column(Integer)                  # Signal strength
    source = Column(String, default="manual")  # "rapt_webhook" or "manual"

    session = relationship("BrewSession", back_populates="fermentation_readings")
    spirit_session = relationship("SpiritRun", back_populates="fermentation_readings")
