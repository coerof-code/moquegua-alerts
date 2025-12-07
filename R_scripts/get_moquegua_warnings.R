# Moquegua Alert Extraction Script for GitHub Actions
# Standalone version - no local dependencies

library(geoidep)
library(sf)
library(dplyr)

# Disable s2 for compatibility
sf::sf_use_s2(FALSE)

# Get the meteorological alerts table
message("Getting meteorological table...")
alerts_table <- senamhi_get_meteorological_table()

# Filter for active alerts (End Date >= Today)
alerts_table$fin_date <- as.Date(alerts_table$fin)
today <- Sys.Date()
alerts_table <- dplyr::filter(alerts_table, fin_date >= today)
message(paste("Active alerts:", nrow(alerts_table)))

# Get district boundaries and filter for Moquegua (Ubigeo 18)
message("Loading district boundaries...")
all_dists <- get_districts(show_progress = FALSE)
moquegua_dists <- all_dists[substr(all_dists$ubigeo, 1, 2) == "18", ]
message(paste("Moquegua districts:", nrow(moquegua_dists)))

# Get province boundaries
message("Loading province boundaries...")
all_provs <- get_provinces(show_progress = FALSE)

# Create province mapping
all_provs$prov_code <- paste0(all_provs$ccdd, all_provs$ccpp)
prov_map <- all_provs %>%
    st_drop_geometry() %>%
    dplyr::select(prov_code, nombprov) %>%
    dplyr::distinct()

# Add Province Name to Districts
moquegua_dists$prov_code <- substr(moquegua_dists$ubigeo, 1, 4)
moquegua_dists <- dplyr::left_join(moquegua_dists, prov_map, by = "prov_code")

# Ensure valid geometries
moquegua_dists <- st_make_valid(moquegua_dists)

# Process each alert
detailed_warnings <- list()

message(paste("Processing", nrow(alerts_table), "alerts..."))

for (i in 1:nrow(alerts_table)) {
    message(paste("  Alert", i, "of", nrow(alerts_table)))
    alert <- alerts_table[i, ]

    # Get spatial data for alert
    alert_geom <- tryCatch(
        {
            senamhi_get_spatial_alerts(data = alert, show_progress = FALSE)
        },
        error = function(e) {
            message(paste("    Error:", e$message))
            NULL
        }
    )

    if (!is.null(alert_geom)) {
        # Validate geometry
        alert_geom <- tryCatch(st_make_valid(alert_geom), error = function(e) NULL)

        if (is.null(alert_geom)) next

        # Filter out "Nivel 1" background geometry
        if ("nivel" %in% names(alert_geom)) {
            alert_geom <- dplyr::filter(alert_geom, nivel != "Nivel 1")
            if (nrow(alert_geom) == 0) next
        }

        # Ensure CRS match
        if (st_crs(moquegua_dists) != st_crs(alert_geom)) {
            alert_geom <- tryCatch(
                st_transform(alert_geom, st_crs(moquegua_dists)),
                error = function(e) NULL
            )
            if (is.null(alert_geom)) next
        }

        # Find intersecting districts
        intersections <- tryCatch(
            st_intersects(moquegua_dists, alert_geom, sparse = FALSE),
            error = function(e) NULL
        )

        if (is.null(intersections)) next

        affected_indices <- which(apply(intersections, 1, any))
        message(paste("    Affected districts:", length(affected_indices)))

        if (length(affected_indices) > 0) {
            affected_dists <- moquegua_dists[affected_indices, ]

            # Create data frame
            affected_areas <- data.frame(
                Aviso = rep(alert$aviso, nrow(affected_dists)),
                Nro = rep(alert$nro, nrow(affected_dists)),
                Nivel = rep(alert$nivel, nrow(affected_dists)),
                Inicio = rep(alert$inicio, nrow(affected_dists)),
                Fin = rep(alert$fin, nrow(affected_dists)),
                Departamento = "MOQUEGUA",
                Provincia = affected_dists$nombprov,
                Distrito = affected_dists$nombdist,
                stringsAsFactors = FALSE
            )

            detailed_warnings <- append(detailed_warnings, list(affected_areas))
        }
    }
}

# Save results
if (length(detailed_warnings) > 0) {
    warnings_df <- do.call(rbind, detailed_warnings)
    warnings_df <- unique(warnings_df)

    message(paste("Total records:", nrow(warnings_df)))

    # Ensure data directory exists
    dir.create("data", showWarnings = FALSE, recursive = TRUE)

    # Save to data/alerts.csv
    write.csv(warnings_df, "data/alerts.csv", row.names = FALSE)
    message("Saved to data/alerts.csv")
} else {
    message("No active alerts found")

    # Create empty CSV with headers
    dir.create("data", showWarnings = FALSE, recursive = TRUE)
    empty_df <- data.frame(
        Aviso = character(),
        Nro = character(),
        Nivel = character(),
        Inicio = character(),
        Fin = character(),
        Departamento = character(),
        Provincia = character(),
        Distrito = character(),
        stringsAsFactors = FALSE
    )
    write.csv(empty_df, "data/alerts.csv", row.names = FALSE)
    message("Created empty alerts.csv")
}
